# Risk Willingness Score — Implementation Specification

## Overview

Build a survey module that calculates an investor's **risk willingness score** (psychological/emotional comfort with investment risk). This is one half of a two-dimensional risk profiling system — the other half is "risk capacity" (financial ability), which is handled separately.

The willingness score will be used alongside a capacity score to determine a target portfolio allocation. The **lower of the two scores constrains** the final allocation.

---

## Questions & Answer Choices

There are 10 questions across 3 categories. Each answer has a point value.

### Category 1: Loss Aversion (Q1–Q4)
**Weight: 1.5x** — These are the strongest predictors of actual portfolio behavior.

#### Q1: Portfolio Drop Reaction
**Prompt:** "Your portfolio drops 20% in a single month. What do you do?"
| Answer | Points |
|--------|--------|
| Sell everything and move to cash | 1 |
| Sell some to reduce further losses | 2 |
| Hold and wait for recovery | 3 |
| Buy more at the lower prices | 4 |

#### Q2: Loss Comfort Level
**Prompt:** "You invest $100,000. After one year it's worth $85,000. How do you feel?"
| Answer | Points |
|--------|--------|
| I can't sleep at night, I need to get out | 1 |
| Very uncomfortable, I'm questioning my strategy | 2 |
| Disappointed but I understand markets fluctuate | 3 |
| Unfazed, this is normal and I see an opportunity | 4 |

#### Q3: Loss vs. Missed Gain
**Prompt:** "Which scenario would bother you more?"
| Answer | Points |
|--------|--------|
| Losing $5,000 on an investment | 1 |
| Both would bother me equally | 2 |
| Missing out on a $5,000 gain by not investing | 3 |

**Note:** This question has only 3 choices. Max points = 3.

#### Q4: Gain Protection Instinct
**Prompt:** "Your portfolio has gained 25% over two years. News suggests a possible recession ahead. What do you do?"
| Answer | Points |
|--------|--------|
| Sell and lock in the gains | 1 |
| Sell half to protect some profits | 2 |
| Stay the course with my current allocation | 3 |
| Maintain or increase equity, since I'm investing for the long run | 4 |

---

### Category 2: Self-Assessment (Q5–Q7)
**Weight: 1.0x**

#### Q5: Investor Identity
**Prompt:** "Which statement best describes you as an investor?"
| Answer | Points |
|--------|--------|
| I want to preserve my capital above all else | 1 |
| I want mostly stability with a small amount of growth | 2 |
| I want balanced growth and am willing to accept moderate ups and downs | 3 |
| I want maximum growth and can handle significant volatility | 4 |

#### Q6: Decision-Making Style
**Prompt:** "When making important financial decisions, how would you characterize your approach?"
| Answer | Points |
|--------|--------|
| I avoid risk whenever possible | 1 |
| I'm cautious but open to modest risk for better returns | 2 |
| I'm comfortable weighing risk against potential reward | 3 |
| I actively seek higher-risk, higher-reward opportunities | 4 |

#### Q7: Relative Risk Appetite
**Prompt:** "Compared to others, how much financial risk are you willing to take?"
| Answer | Points |
|--------|--------|
| Much less than average | 1 |
| Slightly less than average | 2 |
| About average | 3 |
| More than average | 4 |

---

### Category 3: Gambles & Experience (Q8–Q10)
**Weight: Q8 = 1.0x, Q9 = 1.0x, Q10 = 0.75x**

#### Q8: Hypothetical Investment Choice
**Prompt:** "Choose one investment for a $50,000 lump sum:"
| Answer | Points |
|--------|--------|
| Guaranteed 3% annual return | 1 |
| 70% chance of 7% return, 30% chance of 2% return | 2 |
| 50% chance of 12% return, 50% chance of 0% return | 3 |
| 30% chance of 25% return, 70% chance of losing 5% | 4 |

#### Q9: Past Downturn Behavior
**Prompt:** "Think about the worst market downturn you've personally experienced (e.g., COVID crash 2020, 2022 drawdown). What did you actually do?"
| Answer | Points |
|--------|--------|
| I sold most or all of my holdings | 1 |
| I reduced my positions meaningfully | 2 |
| I held steady and did nothing | 3 |
| I added to my positions | 4 |
| I haven't experienced a major downturn yet | **2.5** (special case) |

**Note:** If the investor selects "haven't experienced," score as 2.5 and apply a reduced weight of 0.5x instead of 1.0x for this question.

#### Q10: Investment Experience
**Prompt:** "How many years of investment experience do you have across equities, bonds, or alternatives?"
| Answer | Points |
|--------|--------|
| Less than 2 years | 1 |
| 2–5 years | 2 |
| 5–15 years | 3 |
| More than 15 years | 4 |

---

## Scoring Logic

### Step 1: Apply Weights

```
weighted_score = (Q1 * 1.5) + (Q2 * 1.5) + (Q3 * 1.5) + (Q4 * 1.5)
              + (Q5 * 1.0) + (Q6 * 1.0) + (Q7 * 1.0)
              + (Q8 * 1.0) + (Q9 * Q9_weight) + (Q10 * 0.75)
```

Where `Q9_weight` = 1.0 normally, or 0.5 if the investor selected "haven't experienced a downturn."

### Step 2: Calculate Max Possible Score

```
max_score = (4 * 1.5) + (4 * 1.5) + (3 * 1.5) + (4 * 1.5)
          + (4 * 1.0) + (4 * 1.0) + (4 * 1.0)
          + (4 * 1.0) + (4 * Q9_weight) + (4 * 0.75)

Normal case (Q9_weight=1.0): max = 22.5 + 12 + 4.75 + 4 = 38.75
                              min = 5.625 + 3 + 1.0 + 0.75 = 10.375
Special case (Q9_weight=0.5): max = 22.5 + 12 + 4.75 + 2 = 36.75  (Q9 max = 2.5 * 0.5)
```

### Step 3: Normalize to 0–100

```
normalized_score = ((weighted_score - min_score) / (max_score - min_score)) * 100
```

### Step 4: Map to Willingness Level

| Normalized Score | Willingness Level | Label |
|-----------------|-------------------|-------|
| 0–25 | Low | Conservative |
| 26–50 | Moderate | Balanced |
| 51–75 | Moderately High | Growth |
| 76–100 | High | Aggressive |

---

## Output Schema

The scoring module should return an object like this:

```json
{
  "raw_score": 26.5,
  "max_possible": 38.75,
  "normalized_score": 56.8,
  "willingness_level": "moderately_high",
  "willingness_label": "Growth",
  "category_scores": {
    "loss_aversion": {
      "raw": 10.5,
      "max": 22.5,
      "normalized": 46.7
    },
    "self_assessment": {
      "raw": 9.0,
      "max": 12.0,
      "normalized": 75.0
    },
    "experience_gambles": {
      "raw": 7.0,
      "max": 8.75,
      "normalized": 80.0
    }
  },
  "flags": [
    "inconsistency: self_assessment is aggressive but loss_aversion is conservative"
  ],
  "suggested_equity_range": {
    "min_pct": 60,
    "max_pct": 80
  },
  "answers": {
    "Q1": { "selected": "c", "points": 3, "weight": 1.5 },
    ...
  }
}
```

---

## Suggested Equity Allocation Ranges (Willingness Only)

These are starting points — the capacity score may override them downward.

| Willingness Level | Equity Range | Alternatives Range |
|---|---|---|
| Low (Conservative) | 20–40% | 0–5% |
| Moderate (Balanced) | 40–60% | 5–10% |
| Moderately High (Growth) | 60–80% | 10–20% |
| High (Aggressive) | 75–95% | 15–30% |

---

## Consistency Flags

Flag the following inconsistencies for advisor review:

1. **Loss aversion vs. self-assessment mismatch:** If the loss aversion category (Q1–Q4) normalized score differs from the self-assessment category (Q5–Q7) normalized score by more than 40 points, flag it. Example: "Investor self-identifies as aggressive but shows strong loss aversion in scenario questions."

2. **Past behavior vs. hypothetical mismatch:** If Q9 (actual past behavior) is 2+ points lower than Q1 (hypothetical future behavior), flag it. This suggests the investor overestimates their tolerance. In this case, bias the final score toward Q9 (past behavior is more predictive).

3. **Low experience + high risk appetite:** If Q10 = 1 (< 2 years experience) and normalized score > 75, flag as "limited experience may not support stated risk appetite."

---

## Integration with Capacity Score

This module produces ONLY the willingness score. A separate module handles capacity (time horizon, liquidity needs, income stability, liabilities, portfolio as % of net worth, dependents).

The final target allocation is determined by:

```
final_allocation_level = min(willingness_level, capacity_level)
```

If willingness = "Aggressive" but capacity = "Conservative", the target allocation is **Conservative**.

---

## Research Backing

The question design draws from:

- **Grable & Lytton (1999):** Foundational 13-item psychometric risk tolerance scale. Categories: guaranteed vs. probable gambles, general risk choice, loss aversion, experience, comfort level, speculative risk, prospect theory, investment risk. Cronbach's alpha = 0.77 across 160K+ respondents.
- **Guillemette & Finke (2012, FPA):** Found that loss aversion and self-assessment questions are the best predictors of portfolio allocation. Conventional economic theory questions add little when these two categories are already included. This is why Category 1 is weighted 1.5x.
- **Kahneman & Tversky — Prospect Theory:** People feel losses ~2x as intensely as equivalent gains. Q1–Q4 are rooted in this.
- **SCF Risk Tolerance Scale:** The self-assessment approach (Q5–Q7) has demonstrated face validity through its graded relationship with actual portfolio allocation.
- **Sahm (2007):** 73% of systematic variation in risk tolerance is trait-based and stable over time, supporting the reliability of questionnaire-based measurement. However, re-assessment every 1–2 years is recommended since macroeconomic conditions and aging do shift scores.
- **Swedroe's Capacity Framework:** Informs the separate capacity module and the principle that the lower dimension constrains.
- **CFA Institute Framework:** Formalizes the two-dimensional model (willingness vs. capacity as independent dimensions).
