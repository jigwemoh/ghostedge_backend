# 📊 Debate Engine Output - Visual Example

## Full Example Output

### Run Command
```bash
python test_debate_summary.py
```

### Console Output

```
════════════════════════════════════════════════════════════════════════════════
🤖 GHOSTEDGE AI DEBATE ENGINE - ENHANCED SUMMARY TEST
════════════════════════════════════════════════════════════════════════════════

Starting debate with all three agents...

🤖 Starting Debate for Manchester City...
   👤 statistician: Home 33% | Limited H2H history available.
   👤 tactician: Home 65% | Manchester City has a strong home advantage...
   👤 sentiment_analyst: Home 65% | Manchester City are the clear favorites...

════════════════════════════════════════════════════════════════════════════════
🎯 CONSENSUS DEBATE SUMMARY
════════════════════════════════════════════════════════════════════════════════

📌 MATCH: Manchester City vs West Ham

┌──────────────────────────────────────────────────────────────────────────────┐
│ 👥 AGENT ANALYSES (Individual Predictions)                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ 1. 📊 STATISTICIAN (Weight: 1.5x)                                            │
│    Prediction: Manchester City 33.0% | Draw 33.0% | West Ham 34.0%         │
│    Confidence: 80%                                                           │
│    Reasoning: Limited H2H history available.                                 │
│                                                                              │
│ 2. 🎯 TACTICIAN (Weight: 1.0x)                                              │
│    Prediction: Manchester City 65.0% | Draw 20.0% | West Ham 15.0%         │
│    Confidence: 85%                                                           │
│    Reasoning: Manchester City has a strong home advantage, with a            │
│               high win rate at the Etihad Stadium. Their attacking           │
│               prowess and depth in squad often overwhelm opponents,          │
│               while West Ham has struggled against top-tier teams           │
│               in recent encounters. The probability reflects City's          │
│               superior form and historical performance...                    │
│                                                                              │
│ 3. 😊 SENTIMENT_ANALYST (Weight: 0.8x)                                      │
│    Prediction: Manchester City 65.0% | Draw 20.0% | West Ham 15.0%         │
│    Confidence: 80%                                                           │
│    Reasoning: Manchester City are the clear favorites in this match.        │
│               They have a strong home record and have been in               │
│               excellent form this season, sitting at the top of the         │
│               Premier League table. West Ham have had a mixed start          │
│               to the season and may struggle to match City's quality...      │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│ 🔄 WEIGHTED CONSENSUS CALCULATION                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ 📊 statistician         (1.5x): H:0.495 D:0.495 A:0.510                    │
│ 🎯 tactician            (1.0x): H:0.650 D:0.200 A:0.150                    │
│ 😊 sentiment_analyst    (0.8x): H:0.520 D:0.160 A:0.120                    │
│ ──────────────────────────────────────────────────────────────────────────── │
│ Total Weight: 3.3x                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ ✅ FINAL CONSENSUS PREDICTION                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Manchester City            50.00%  ████████░░░                              │
│ Draw                       26.00%  ███░░░░░░░░                              │
│ West Ham                   24.00%  ██░░░░░░░░                               │
│                                                                              │
│ 🏆 Most Likely Outcome: Manchester City Win (50.0%)                         │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════
📊 AGREEMENT & CONFIDENCE METRICS
════════════════════════════════════════════════════════════════════════════════
Confidence Score: 93%
Agreement Score: 36%

════════════════════════════════════════════════════════════════════════════════
📋 DETAILED AGENT ANALYSES
════════════════════════════════════════════════════════════════════════════════

STATISTICIAN (Weight: 1.5x):
  Prediction: H=33% D=33% A=34%
  Confidence: 80%
  Weighted Contribution: H=0.495 D=0.495 A=0.510
  Reasoning: Limited H2H history available.

TACTICIAN (Weight: 1.0x):
  Prediction: H=65% D=20% A=15%
  Confidence: 85%
  Weighted Contribution: H=0.650 D=0.200 A=0.150
  Reasoning: Manchester City has a strong home advantage, with a high win 
             rate at the Etihad Stadium...

SENTIMENT_ANALYST (Weight: 0.8x):
  Prediction: H=65% D=20% A=15%
  Confidence: 80%
  Weighted Contribution: H=0.520 D=0.160 A=0.120
  Reasoning: Manchester City are the clear favorites in this match. They
             have a strong home record and have been in excellent form...

════════════════════════════════════════════════════════════════════════════════
📤 FULL API RESPONSE (JSON)
════════════════════════════════════════════════════════════════════════════════
{
  "consensus_prediction": {
    "home_win": 0.50,
    "draw": 0.26,
    "away_win": 0.24
  },
  "confidence": 0.93,
  "agreement_score": 0.36,
  "agent_analyses": [
    {
      "agent": "statistician",
      "weight": "1.5x",
      "prediction": {
        "home_win": 0.33,
        "draw": 0.33,
        "away_win": 0.34
      },
      "confidence": 0.8,
      "reasoning": "Limited H2H history available.",
      "weighted_contribution": {
        "home_win": 0.495,
        "draw": 0.495,
        "away_win": 0.51
      }
    },
    {
      "agent": "tactician",
      "weight": "1.0x",
      "prediction": {
        "home_win": 0.65,
        "draw": 0.2,
        "away_win": 0.15
      },
      "confidence": 0.85,
      "reasoning": "Manchester City has a strong home advantage, with a...",
      "weighted_contribution": {
        "home_win": 0.65,
        "draw": 0.2,
        "away_win": 0.15
      }
    },
    {
      "agent": "sentiment_analyst",
      "weight": "0.8x",
      "prediction": {
        "home_win": 0.65,
        "draw": 0.2,
        "away_win": 0.15
      },
      "confidence": 0.8,
      "reasoning": "Manchester City are the clear favorites in this match...",
      "weighted_contribution": {
        "home_win": 0.52,
        "draw": 0.16,
        "away_win": 0.12
      }
    }
  ]
}
```

---

## Key Insights From Example

### Agent Predictions

| Agent | H-Win | Draw | A-Win | Confidence | Weight |
|-------|-------|------|-------|-----------|--------|
| 📊 Statistician | 33% | 33% | 34% | 80% | 1.5x |
| 🎯 Tactician | 65% | 20% | 15% | 85% | 1.0x |
| 😊 Sentiment | 65% | 20% | 15% | 80% | 0.8x |
| **Final** | **50%** | **26%** | **24%** | **93%** | **3.3x** |

### Weighted Calculation Breakdown

```
Home Win:
  Statistician: 0.33 × 1.5 = 0.495
  Tactician:    0.65 × 1.0 = 0.650
  Sentiment:    0.65 × 0.8 = 0.520
  Total:        (0.495 + 0.650 + 0.520) / 3.3 = 0.50 (50%)

Draw:
  Statistician: 0.33 × 1.5 = 0.495
  Tactician:    0.20 × 1.0 = 0.200
  Sentiment:    0.20 × 0.8 = 0.160
  Total:        (0.495 + 0.200 + 0.160) / 3.3 = 0.26 (26%)

Away Win:
  Statistician: 0.34 × 1.5 = 0.510
  Tactician:    0.15 × 1.0 = 0.150
  Sentiment:    0.15 × 0.8 = 0.120
  Total:        (0.510 + 0.150 + 0.120) / 3.3 = 0.24 (24%)
```

### Analysis

- **Agreement Score: 36%** - Low agreement between statistician (33%) and others (65%)
  - Statistician has limited H2H data
  - Tactician and Sentiment strongly agree on 65%

- **Confidence Score: 93%** - High confidence despite lower agreement
  - High variance is offset by consistent tactical/sentiment views
  - Final prediction (50%) is a reasonable compromise

- **Prediction: Manchester City 50% Win** - Even with disagreement, City is favored
  - Weighted heavily toward Tactician & Sentiment (both 65%)
  - Statistician brings down the prediction due to lower confidence in H2H data

---

## What's Displayed

✅ **Agent Icons** - Easy identification of each agent
✅ **Individual Predictions** - What each agent predicts
✅ **Agent Confidence** - How confident each agent is
✅ **Detailed Reasoning** - Full explanation from each agent
✅ **Weighted Calculation** - Mathematical breakdown
✅ **Final Consensus** - Overall prediction
✅ **Probability Bars** - Visual representation
✅ **Agreement Metrics** - System confidence and agent agreement
✅ **Most Likely Outcome** - Winner prediction

---

## How to Integrate

The enhanced debate output is automatically returned by:

```python
from w5_engine.debate import ConsensusEngine

engine = ConsensusEngine()
result = engine.run_consensus(match_data)

# result contains:
# - consensus_prediction (final probabilities)
# - confidence (0-1 score)
# - agreement_score (0-1 score)
# - debate_summary (formatted string)
# - agent_analyses (detailed array)
```

---

## Files Modified

- `w5_engine/debate.py` - Enhanced with summary methods
- `test_debate_summary.py` - Test script showing full output

**Commit:** `21478b0`
