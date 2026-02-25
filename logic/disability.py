import pandas as pd
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

class PolicyMetadata(BaseModel):
    insurer_name: str
    policy_type: str

class BenefitParameters(BaseModel):
    replacement_percentage: float
    maximum_monthly_benefit: float
    minimum_monthly_benefit: float
    elimination_period_days: int
    max_benefit_duration: str

class EarningsDefinition(BaseModel):
    includes_base_salary: bool
    includes_bonuses: bool
    includes_commissions: bool
    includes_overtime: bool

class DisabilityDefinition(BaseModel):
    own_occupation_period_months: int

class DeductibleOffsets(BaseModel):
    offsets_primary_ssdi: bool
    offsets_family_ssdi: bool
    offsets_workers_comp: bool
    offsets_state_disability: bool

class GroupDisabilityPolicy(BaseModel):
    policy_metadata: PolicyMetadata
    benefit_parameters: BenefitParameters
    earnings_definition: EarningsDefinition
    disability_definition: DisabilityDefinition
    deductible_offsets: DeductibleOffsets

def calculate_ssdi_pia_2026(aime: float) -> float:
    """Calculates the 2026 Primary Insurance Amount (PIA) for SSDI."""
    BEND_POINT_1 = 1286.0
    BEND_POINT_2 = 7749.0
    FACTOR_1, FACTOR_2, FACTOR_3 = 0.90, 0.32, 0.15
    
    if aime <= 0: return 0.0
        
    if aime <= BEND_POINT_1:
        pia = aime * FACTOR_1
    elif aime <= BEND_POINT_2:
        pia = (BEND_POINT_1 * FACTOR_1) + ((aime - BEND_POINT_1) * FACTOR_2)
    else:
        pia = (BEND_POINT_1 * FACTOR_1) + ((BEND_POINT_2 - BEND_POINT_1) * FACTOR_2) + ((aime - BEND_POINT_2) * FACTOR_3)
              
    return int(pia * 10) / 10.0 # Truncate to next lower dime

class DisabilityCashFlowModel:
    def __init__(self, policy: GroupDisabilityPolicy, user_inputs: dict):
        self.policy = policy
        self.inputs = user_inputs
        
    def calculate_insurable_earnings(self) -> float:
        monthly_earnings = 0.0
        ed = self.policy.earnings_definition
        any_component_flagged = (
            ed.includes_base_salary or ed.includes_bonuses
            or ed.includes_commissions or ed.includes_overtime
        )

        if any_component_flagged:
            # Use only the explicitly included components
            if ed.includes_base_salary:
                monthly_earnings += self.inputs.get('annual_base_salary', 0) / 12
            if ed.includes_bonuses:
                monthly_earnings += self.inputs.get('annual_bonus', 0) / 12
        else:
            # No components explicitly flagged by the LLM — fall back to
            # treating all provided earnings as covered (base + bonus).
            monthly_earnings = (
                self.inputs.get('annual_base_salary', 0)
                + self.inputs.get('annual_bonus', 0)
            ) / 12

        return monthly_earnings

    def _normalize_replacement_rate(self) -> float:
        """Return the replacement rate as a decimal (e.g. 0.60 for 60%)."""
        rate = self.policy.benefit_parameters.replacement_percentage
        # If the LLM returned a percentage value (e.g. 60), convert to decimal
        if rate > 1:
            return rate / 100.0
        return rate

    def generate_timeline(self) -> pd.DataFrame:
        disability_date = pd.Timestamp(self.inputs['date_of_disability'])
        dob = pd.Timestamp(self.inputs['date_of_birth'])
        
        ep_days = self.policy.benefit_parameters.elimination_period_days
        benefit_start_date = disability_date + relativedelta(days=ep_days)
        benefit_end_date = dob + relativedelta(years=65) # Approximation for SSNRA
        
        date_range = pd.date_range(start=disability_date, end=benefit_end_date, freq='MS')
        df = pd.DataFrame(index=date_range)
        df['Month_Index'] = range(1, len(df) + 1)
        
        # 1. Map Gross Benefit
        insurable_earnings = self.calculate_insurable_earnings()
        replacement_rate = self._normalize_replacement_rate()
        gross_benefit = min(
            insurable_earnings * replacement_rate,
            self.policy.benefit_parameters.maximum_monthly_benefit
        )
        df['Gross_Benefit'] = np.where(df.index >= benefit_start_date, gross_benefit, 0.0)
        
        # 2. Map Offsets
        if self.policy.deductible_offsets.offsets_primary_ssdi:
            ssdi_amount = calculate_ssdi_pia_2026(self.inputs.get('aime', 0))
            ssdi_start_date = disability_date + relativedelta(months=5) # 5-month statutory wait
            df['SSDI_Offset'] = np.where(df.index >= ssdi_start_date, ssdi_amount, 0.0)
        else:
            df['SSDI_Offset'] = 0.0

        if self.policy.deductible_offsets.offsets_workers_comp:
            wc_amount = self.inputs.get('monthly_workers_comp', 0.0)
            df['Workers_Comp_Offset'] = np.where(df.index >= disability_date, wc_amount, 0.0)
        else:
            df['Workers_Comp_Offset'] = 0.0

        df['Total_Offsets'] = df['SSDI_Offset'] + df['Workers_Comp_Offset']

        # 3. Calculate Net Benefit
        min_benefit = self.policy.benefit_parameters.minimum_monthly_benefit
        raw_net_benefit = df['Gross_Benefit'] - df['Total_Offsets']
        
        df['Net_Payout'] = np.where(
            df['Gross_Benefit'] > 0, 
            np.maximum(raw_net_benefit, min_benefit), 
            0.0
        )
        
        return df
