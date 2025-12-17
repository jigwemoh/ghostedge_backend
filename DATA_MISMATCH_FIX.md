# Data Mismatch Issue - Diagnosis & Solution

## Problem Identified ❌

Your pipeline is receiving **incorrect team IDs** that don't match the team names:

```json
{
  "home_team": "Man City",
  "away_team": "West Ham",
  "home_team_id": 8456,           ← WRONG: This is Worgl (Austrian team)
  "away_team_id": 8654,           ← WRONG: This is Asenovets (Bulgarian team)
  "league_id": 47
}
```

Result: The API returns data for Worgl and Asenovets instead of Man City and West Ham!

```json
{
  "home_venue": "Sportstadion Worgl (Worgl)",  ← Wrong stadium
  "away_venue": "Stadion Shipka",              ← Wrong stadium
  "home_recent_signings": 0,                   ← Wrong player data
  "away_recent_signings": 0
}
```

## Root Cause

The **team IDs in your data source are incorrect**. The IDs come from your frontend/data provider, not from our code. The problem is:

1. **Frontend/Data Source** provides wrong team IDs (8456, 8654)
2. **Loader validates** but can't fix them - they're just wrong
3. **Soccerdata API** returns correct data FOR those IDs (Worgl, Asenovets)
4. **Pipeline displays** mismatch clearly: Expected Man City, Got Worgl

## Solution Steps

### Step 1: Find Correct Team IDs

Use the included `find_team_ids.py` script to get correct IDs:

```bash
python find_team_ids.py "Manchester City"
python find_team_ids.py "West Ham"
```

Example output:
```
🔍 Searching for team: Manchester City
✅ Found 1 result(s):

  1. Manchester City - ID: 123 (Premier League)

🏟️ Stadium: Etihad Stadium
   Capacity: 55,097
```

### Step 2: Fix Your Data Source

Update wherever your team IDs come from:
- **If using RapidAPI**: Map their team IDs to Soccerdata IDs
- **If using database**: Update team ID mappings
- **If hardcoded**: Replace with correct IDs from step 1

### Step 3: Validate Before Processing

Before sending matches to the pipeline, validate them:

```bash
python validate_match_data.py match_data.json
```

This will show:
```
✅ VALIDATION PASSED - All data looks correct!
```

or

```
❌ VALIDATION FAILED - 2 issue(s) found:
   1. Home team ID 8456 is for Worgl, not Manchester City
```

## Team ID Reference for Major Teams

### Premier League (League ID: 39)
```
Manchester City:   50
Liverpool:         64
Arsenal:           42
Manchester United: 33
Chelsea:           49
Tottenham:         47
...
```

### La Liga (League ID: 140)
```
Real Madrid:       418
Barcelona:         206
Atletico Madrid:   7
Sevilla:           541
...
```

To get complete list:
```bash
python find_team_ids.py "" 39    # All Premier League teams
```

## Validation Output Interpretation

### ✅ All Good
```
✅ Found: Manchester City
✅ Name matches
✅ Stadium: Etihad Stadium
```
→ Proceed with pipeline

### ⚠️ Name Mismatch
```
❌ Could not find team with ID 8456
```
or
```
⚠️ NAME MISMATCH: Expected 'Man City' but got 'Worgl'
```
→ Use `find_team_ids.py` to get correct ID

### ❌ Stadium Issues
```
⚠️ Stadium: Not found
```
→ Team ID is likely wrong, validate it

## How to Fix Your Data Pipeline

### Option A: Fix at Data Source (Best)
Update your backend/database to use correct team IDs:

```python
# BEFORE (Wrong)
{
  "home_team": "Man City",
  "home_team_id": 8456,  # ← Worgl, not Man City
}

# AFTER (Correct)
{
  "home_team": "Man City",
  "home_team_id": 50,    # ← Correct ID for Man City
}
```

### Option B: Add Mapping Layer
If you can't change the source, add a mapping layer:

```python
TEAM_ID_MAP = {
    "Manchester City": 50,
    "West Ham": 48,
    "Liverpool": 64,
    # ... etc
}

# In main.py
correct_home_id = TEAM_ID_MAP.get(match.home_team_name, match.home_team_id)
correct_away_id = TEAM_ID_MAP.get(match.away_team_name, match.away_team_id)

match_context = real_data_loader.fetch_full_match_context(
    home_team=match.home_team_name,
    away_team=match.away_team_name,
    event_id=match.event_id,
    league_id=match.league_id,
    home_team_id=correct_home_id,    # ← Use corrected ID
    away_team_id=correct_away_id     # ← Use corrected ID
)
```

### Option C: Auto-Lookup (Slower but works)
Have the loader automatically search for correct IDs:

```python
# Modify fetch_full_match_context to search if IDs don't match
if not self._validate_team_id(home_team_id, home_team):
    print(f"⚠️ Team ID mismatch, searching for {home_team}...")
    results = self.soccerdata_client.search_team_by_name(
        home_team, 
        league_id
    )
    if results:
        home_team_id = results[0]['id']
        print(f"✅ Found correct ID: {home_team_id}")
```

## Quick Diagnostic Checklist

- [ ] Run validation script: `python validate_match_data.py`
- [ ] Check error message for mismatched team name
- [ ] Run `python find_team_ids.py "Team Name"` to get correct ID
- [ ] Update data source with correct ID
- [ ] Run validation again to confirm fix

## Tools Available

| Tool | Purpose | Command |
|------|---------|---------|
| `find_team_ids.py` | Find correct team IDs | `python find_team_ids.py "Team Name"` |
| `validate_match_data.py` | Validate match data | `python validate_match_data.py data.json` |
| Loader validation | Check during processing | Built-in warnings printed |

## Expected Correct Output

After fixing the team IDs, you should see:

```json
{
  "match_id": "4813541",
  "home_team": "Man City",
  "away_team": "West Ham",
  "quantitative_features": {
    "h2h_overall_games": 48,
    "h2h_team1_wins": 26,
    "h2h_team1_win_pct": 54.2,
    "league_leader_points": 80,
    "home_recent_signings": 4,
    "away_recent_signings": 2
  },
  "qualitative_context": {
    "home_venue": "Etihad Stadium",
    "home_capacity": 55097,
    "away_venue": "London Stadium",
    "away_capacity": 62500,
    "weather": "Partly Cloudy, 65°F"
  }
}
```

## Prevention

Going forward:

1. **Always validate** team IDs before processing
2. **Use mapping** if data source has different ID system
3. **Test** with known good matches first
4. **Monitor** warnings in loader output

---

**Status**: Data validation tools created and working  
**Next Step**: Identify source of team IDs and fix the mapping
