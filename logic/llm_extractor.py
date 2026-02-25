import os
import json
import tempfile
import streamlit as st
from google import genai
from google.genai import types
from pydantic import ValidationError
from .disability import GroupDisabilityPolicy


def _get_gemini_api_key() -> str:
    """Retrieve the Gemini API key from Streamlit secrets (Cloud/local) or env var."""
    # 1. Streamlit secrets (works on Cloud + locally via .streamlit/secrets.toml)
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass

    # 2. Fall back to environment variable
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    raise RuntimeError(
        "GEMINI_API_KEY not found. Set it in .streamlit/secrets.toml "
        "or as an environment variable."
    )

SYSTEM_PROMPT = """You are an expert insurance actuary and data extraction assistant specializing in Group Long-Term Disability (LTD) policies. 

Your objective is to extract specific financial and contractual parameters from the provided disability insurance document and format them STRICTLY according to the JSON schema provided below.

INSTRUCTIONS:
1. Locate the precise numerical values for the Benefit Percentage, Maximum Monthly Benefit, Minimum Monthly Benefit, Elimination Period (in days), and Maximum Benefit Duration.
2. Identify exactly which types of compensation (Base Salary, Bonuses, Commissions, Overtime) are explicitly included or excluded in the definition of "Pre-Disability Earnings".
3. Identify the duration of the "Own Occupation" period (e.g., 24 months).
4. Identify which "Other Income" sources are explicitly listed as offsets (e.g., Primary Social Security, Dependent/Family Social Security, Workers' Compensation, State Disability).
5. Output ONLY valid JSON. If a value is not explicitly stated, use `null` or `false`.
"""

def extract_disability_policy(file_content: bytes, file_name: str = "document.pdf") -> GroupDisabilityPolicy:
    # Initialize the client with the API key from secrets/env
    api_key = _get_gemini_api_key()
    client = genai.Client(api_key=api_key)
    
    # Write content to a temp file so the Gemini SDK can upload it
    suffix = os.path.splitext(file_name)[1] or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        # Upload the temp file to Gemini
        uploaded_file = client.files.upload(file=tmp_path)
        
        try:
            # Call the model
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    uploaded_file,
                    "Extract the disability policy details from this document."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=GroupDisabilityPolicy,
                    temperature=0.1,
                ),
            )
            
            # Parse the JSON response
            if hasattr(response, 'parsed') and response.parsed:
                return response.parsed
                
            data = json.loads(response.text)
            
            # Validate with Pydantic
            policy = GroupDisabilityPolicy(**data)
            return policy
            
        finally:
            # Clean up the uploaded file from Gemini
            client.files.delete(name=uploaded_file.name)
    finally:
        # Clean up the temp file from disk
        os.unlink(tmp_path)
