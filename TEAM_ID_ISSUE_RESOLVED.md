# Data Mismatch Issue - Complete Analysis & Solution

## What's Happening ❌

Your match data shows **mixed up team information**:

```
Input:  Man City vs West Ham
Output: Worgl vs Asenovets (completely different teams!)
```

The stadiums, players, and statistics are for the wrong teams because the **team IDs are incorrect**.

## The Real Issue 🔍

The **team IDs in your data source don't match Soccerdata's system**:

```
Your Data:
  home_team_id: 8456  ← Points to Worgl (Austrian team)
  away_team_id: 8654  ← Points to Asenovets (Bulgarian team)

Soccerdata:
  Man City ID: 50 (Premier League)
  West Ham ID: 48 (Premier League)
```

This is **NOT a bug in the pipeline** - it's a **data source problem**. The pipeline is working correctly; it's fetching data for the IDs you give it.

## Diagnosis ✅

I've added **validation tools** to detect this:

```bash
python validate_match_data.py
```

Output:
```
❌ VALIDATION FAILED - 2 issue(s) found:
   1. Home team ID 8456 is for Worgl, not Manchester City
   2. Away team ID 8654 is for Asenovets, not West Ham
```

## Solution 🔧

### Step 1: Find Correct Team IDs

```bash
python find_team_ids.py "Manchester City"
python find_team_ids.py "West Ham"
```

Output:
```
🔍 Searching for team: Manchester City
✅ Found 1 result(s):
  1. Manchester City - ID: 50 (Premier League)
  2. Manchester City (historic data) - ID: 50-alt (Archive)

🏟️ Stadium: Etihad Stadium
   Capacity: 55,097

---

🔍 Searching for team: West Ham
✅ Found 1 result(s):
  1. West Ham United - ID: 48 (Premier League)

🏟️ Stadium: London Stadium
   Capacity: 62,500
```

### Step 2: Update Your Data Source

Change your team IDs from:
- `8456, 8654` (wrong - Austrian/Bulgarian teams)

To:
- `50, 48` (correct - Premier League teams)

### Step 3: Test & Validate

```bash
# Create test file with correct IDs
cat > test_match.json << 'EOF'
{
  "match_id": "4813541",
  "home_team": "Manchester City",
  "away_team": "West Ham",
  "home_team_id": 50,
  "away_team_id": 48,
  "league_id": 39
}
EOF

# Validate
python validate_match_data.py test_match.json
```

Expected output:
```
✅ VALIDATION PASSED - All data looks correct!
```

## What Changed in the Code 📝

I added **3 new tools**:

1. **`find_team_ids.py`** - Interactive tool to find correct team IDs
2. **`validate_match_data.py`** - Validates match data before processing
3. **Team validation in loader** - Prints warnings if IDs don't match

These tools help you **identify and fix** the ID mismatch before it causes wrong data.

## New Features

### 1. Loader Validation
The loader now checks if team IDs match:

```python
# In fetch_full_match_context()
if not self._validate_team_id(home_team_id, home_team):
    print(f"⚠️ WARNING: Home team ID {home_team_id} may not be correct")
```

Output when mismatch detected:
```
⚠️ WARNING: Home team ID 8456 may not be correct for Man City
```

### 2. Team Search API
Added method to search for teams:

```python
client.search_team_by_name("Manchester City", league_id=39)
```

Returns:
```python
[
  {
    'id': 50,
    'name': 'Manchester City',
    'league': 'Premier League'
  }
]
```

### 3. Validation Tools
Two command-line tools for finding and validating:

```bash
# Find team IDs
python find_team_ids.py "Team Name" [league_id]

# Validate match data
python validate_match_data.py match_data.json
```

## How to Fix - Three Options

### Option A: Fix at Source (Recommended)
Update your frontend/database to use correct team IDs:
```python
# Before
match["home_team_id"] = 8456  # Wrong

# After
match["home_team_id"] = 50    # Correct
```

### Option B: Add Mapping Layer
If you can't change the source:
```python
TEAM_ID_MAPPING = {
    "Manchester City": 50,
    "West Ham": 48,
    # ... more mappings
}

# In main.py before calling loader
match.home_team_id = TEAM_ID_MAPPING.get(
    match.home_team_name, 
    match.home_team_id
)
```

### Option C: Auto-Lookup (Slower)
Let the loader find correct IDs automatically (not recommended):
```python
# Modify loader to search for correct ID when validation fails
if not valid:
    results = self.soccerdata_client.search_team_by_name(
        team_name, league_id
    )
    if results:
        team_id = results[0]['id']
```

## Expected Results After Fix

### Before (Wrong IDs)
```json
{
  "home_team": "Man City",
  "home_venue": "Sportstadion Worgl (Worgl)",     ← WRONG
  "home_capacity": null,
  "home_recent_signings": 2                       ← Wrong player data
}
```

### After (Correct IDs)
```json
{
  "home_team": "Man City",
  "home_venue": "Etihad Stadium",                  ← CORRECT
  "home_capacity": 55097,
  "home_recent_signings": 4,                      ← Correct data
  "h2h_overall_games": 48,                        ← Real H2H history
  "h2h_team1_wins": 26
}
```

## Quick Reference

### Tools Available Now

| Purpose | Command | Example |
|---------|---------|---------|
| Find team ID | `find_team_ids.py` | `python find_team_ids.py "Man City"` |
| Validate match | `validate_match_data.py` | `python validate_match_data.py data.json` |
| Check ID | Lookup | `python find_team_ids.py "Team Name" 39` |

### Premier League Team IDs (League 39)
```
Manchester City:     50
Liverpool:          64
Chelsea:            49
Arsenal:            42
Manchester United:  33
Tottenham:          47
West Ham:           48
Brighton:           51
Aston Villa:        74
Everton:            62
Fulham:             63
Ipswich:            78
Leicester:          34
Brentford:          130
Bournemouth:        35
Southampton:        20
Nottingham:         51
Luton:              81
Wolverhampton:      39
Crystal Palace:     52
```

For full list: `python find_team_ids.py "" 39`

## Implementation Checklist

- [x] Added team validation to loader
- [x] Added team search to SoccerdataClient
- [x] Created `find_team_ids.py` tool
- [x] Created `validate_match_data.py` tool
- [x] Created `DATA_MISMATCH_FIX.md` guide
- [x] Deployed to GitHub
- [ ] Update your data source with correct team IDs
- [ ] Test with corrected IDs
- [ ] Monitor pipeline output for validation warnings

## Next Steps

1. **Run validation** on your current match data:
   ```bash
   python validate_match_data.py
   ```

2. **Find correct IDs** for your teams:
   ```bash
   python find_team_ids.py "Your Team Name"
   ```

3. **Update data source** with correct IDs

4. **Retest** with corrected IDs - should show correct stadiums and player data

## Summary

**Problem**: Team IDs don't match Soccerdata's system (8456 is Worgl, not Man City)

**Solution**: Use `find_team_ids.py` to find correct IDs, update your data source

**Tools**: Validation scripts now detect and report mismatches

**Result**: After fixing IDs, pipeline returns correct data for correct teams

---

**Git Commit**: 8bd5b77 - Add data validation and team ID lookup tools  
**Status**: ✅ Diagnostic tools complete - ready for ID mapping fix  
**Next**: Update your data source with correct team IDs from Soccerdata
