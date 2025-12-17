# Soccerdata API Integration - Documentation Index

Welcome! Here's your guide to navigating the Soccerdata API integration for the ConsensusEngine.

---

## 📍 Where to Start

### If you want to...

**🚀 Get up and running quickly**
→ Run: `python quickstart.py`
→ Read: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) (5-10 min read)

**📚 Understand the full API**
→ Read: [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md) (20-30 min read)

**💻 See code examples**
→ Check: [w5_engine/api_usage_examples.py](w5_engine/api_usage_examples.py)

**📝 Understand what changed**
→ Read: [CHANGELOG.md](CHANGELOG.md)

**🔧 Set up the integration**
→ Follow setup section in [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 📂 File Organization

### Documentation Files
```
/
├── SOCCERDATA_API_INTEGRATION.md    ← Complete API reference
├── IMPLEMENTATION_SUMMARY.md         ← Quick start guide
├── CHANGELOG.md                      ← What changed
├── README_API_INTEGRATION.md         ← This file
└── quickstart.py                     ← Verification script
```

### Code Files
```
w5_engine/
├── soccerdata_client.py              ← API client (NEW)
├── api_usage_examples.py             ← Examples (NEW)
└── debate.py                         ← Updated engine
```

---

## 🎯 Quick Navigation

### API Documentation
- **All 14 Endpoints** → [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md#-available-api-endpoints)
- **Setup Instructions** → [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md#setup)
- **Usage Examples** → [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md#usage-examples)
- **Team/League IDs** → [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md#team-ids-reference)

### Code
- **SoccerdataClient** → [w5_engine/soccerdata_client.py](w5_engine/soccerdata_client.py)
- **API Examples** → [w5_engine/api_usage_examples.py](w5_engine/api_usage_examples.py)
- **Updated Engine** → [w5_engine/debate.py](w5_engine/debate.py)

### Reference
- **What's New** → [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Changes Log** → [CHANGELOG.md](CHANGELOG.md)

---

## 🚀 Quick Start (5 minutes)

### Step 1: Get API Key (2 min)
1. Visit https://soccerdataapi.com
2. Sign up for free account
3. Get your `auth_token` API key

### Step 2: Configure Environment (1 min)
```bash
cat > .env << EOF
SOCCERDATA_API_KEY=your_key_here
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
EOF
```

### Step 3: Verify Installation (2 min)
```bash
python quickstart.py
```

### Step 4: Use in Code
```python
from w5_engine.debate import ConsensusEngine

engine = ConsensusEngine()
result = engine.run_consensus({
    'home_team': 'Liverpool',
    'home_team_id': 4138,
    'away_team': 'Man United',
    'away_team_id': 4137,
    'league_id': 228,
})

print(f"Home Win: {result['consensus_prediction']['home_win']:.1%}")
```

---

## 📊 What You Get

### Automatic Data Enrichment
When you call `run_consensus()`, it automatically fetches:
- ✅ League standings and positions
- ✅ Head-to-head historical stats
- ✅ Recent transfers for both teams
- ✅ Team stadium information
- ✅ AI-generated match previews
- ✅ Recent match results

### Three AI Agents Analyze:
- **Statistician** (1.5x weight) - Uses hard API data
- **Tactician** (1.0x weight) - Uses OpenAI analysis
- **Sentiment** (0.8x weight) - Uses Anthropic insights

### Weighted Consensus Prediction:
```
Final Prediction = (1.5×Stat + 1.0×Tact + 0.8×Sent) / 3.3
```

---

## 🔗 API Endpoints Available

| # | Endpoint | Purpose | Status |
|---|----------|---------|--------|
| 1 | GET COUNTRY | Countries list | ✅ Ready |
| 2 | GET LEAGUE | Leagues by country | ✅ Ready |
| 3 | GET SEASON | Seasons for league | ✅ Ready |
| 4 | GET STANDING | League table | ✅ Used |
| 5 | GET TEAM | Team information | ✅ Ready |
| 6 | GET STADIUM | Stadium info | ✅ Used |
| 7 | GET PLAYER | Player information | ✅ Ready |
| 8 | GET TRANSFERS | Team transfers | ✅ Used |
| 9 | GET H2H | Head-to-head stats | ✅ Used |
| 10 | GET MATCH | Match details | ✅ Ready |
| 11 | GET MATCHES | Matches list | ✅ Used |
| 12 | GET LIVESCORES | Live matches | ✅ Ready |
| 13 | GET MATCH PREVIEW | AI preview | ✅ Used |
| 14 | GET UPCOMING PREVIEWS | Future matches | ✅ Ready |

---

## 💡 Common Use Cases

### Use Case 1: Simple Prediction
```python
from w5_engine.debate import ConsensusEngine

engine = ConsensusEngine()
result = engine.run_consensus({
    'home_team': 'Arsenal',
    'home_team_id': 3068,
    'away_team': 'Chelsea',
    'away_team_id': 3170,
    'league_id': 228,
})
```

### Use Case 2: Get Specific Stats
```python
from w5_engine.soccerdata_client import SoccerdataClient

client = SoccerdataClient()
h2h = client.get_head_to_head(team_1_id=3068, team_2_id=3170)
standing = client.get_standing(league_id=228)
```

### Use Case 3: Custom Analysis
```python
client = SoccerdataClient()
standing = client.get_standing(league_id=228)
team_stats = client.extract_standing_for_team(228, "Arsenal")
print(f"Arsenal position: {team_stats['position']}")
print(f"Arsenal points: {team_stats['points']}")
```

---

## 🎓 Learning Path

### Beginner
1. Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) (overview)
2. Run `python quickstart.py` (verify setup)
3. Try basic example in [api_usage_examples.py](w5_engine/api_usage_examples.py)

### Intermediate
1. Read [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md) (full guide)
2. Study [soccerdata_client.py](w5_engine/soccerdata_client.py) (implementation)
3. Try all examples in [api_usage_examples.py](w5_engine/api_usage_examples.py)

### Advanced
1. Review [CHANGELOG.md](CHANGELOG.md) (implementation details)
2. Study [debate.py](w5_engine/debate.py) (integration)
3. Implement caching and custom extractors

---

## 🔧 Troubleshooting

### API Key Issues
- **Error:** "SOCCERDATA_API_KEY not found"
- **Solution:** Check `.env` file in project root contains: `SOCCERDATA_API_KEY=your_key`

### No Data Returned
- **Error:** API returns None
- **Solution:** Verify team/league IDs are correct (see [Team IDs Reference](SOCCERDATA_API_INTEGRATION.md#team-ids-reference))

### Slow Responses
- **Error:** API calls taking 10+ seconds
- **Solution:** Normal on first call; implement caching for repeat calls

### Invalid Token
- **Error:** "Invalid token" in API response
- **Solution:** Regenerate API key at https://soccerdataapi.com

For more help → [SOCCERDATA_API_INTEGRATION.md - Troubleshooting](SOCCERDATA_API_INTEGRATION.md#troubleshooting)

---

## 📞 Support Resources

### Official
- **Soccerdata API Docs:** https://soccerdataapi.com/docs
- **Soccerdata Support:** https://soccerdataapi.com/support

### In This Project
- **Full Documentation:** [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md)
- **Quick Reference:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Code Examples:** [w5_engine/api_usage_examples.py](w5_engine/api_usage_examples.py)

---

## 📈 Performance Tips

### Optimization
1. **Cache Results** - Store API responses in SQLite/Redis
2. **Batch Calls** - Fetch multiple leagues/teams in one request
3. **Schedule Updates** - Update standings once per day
4. **Use IDs** - Always use team/league IDs (faster than names)

### Monitoring
- Track API response times
- Monitor API call count (rate limiting)
- Log errors for debugging
- Cache hit/miss ratio

---

## ✅ Setup Checklist

- [ ] Got Soccerdata API key from https://soccerdataapi.com
- [ ] Created `.env` file with `SOCCERDATA_API_KEY`
- [ ] Installed dependencies: `pip install requests python-dotenv`
- [ ] Ran `python quickstart.py` successfully
- [ ] Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- [ ] Tested with sample match data
- [ ] Ready to integrate into your application

---

## 🎯 Integration Status

| Component | Status | Details |
|-----------|--------|---------|
| API Client | ✅ COMPLETE | All 14 endpoints |
| Engine Integration | ✅ COMPLETE | Auto-enrichment |
| Documentation | ✅ COMPLETE | 4 documents |
| Examples | ✅ COMPLETE | 5 examples |
| Testing | ✅ COMPLETE | quickstart.py |
| Production Ready | ✅ YES | Add caching layer |

---

## 📝 File Sizes & Line Counts

| File | Lines | Size | Purpose |
|------|-------|------|---------|
| soccerdata_client.py | 212 | 7.5 KB | API Client |
| api_usage_examples.py | 148 | 5.2 KB | Examples |
| debate.py (added) | +130 | +4.8 KB | Integration |
| SOCCERDATA_API_INTEGRATION.md | ~400 | ~18 KB | Full Guide |
| IMPLEMENTATION_SUMMARY.md | ~200 | ~9 KB | Quick Ref |
| CHANGELOG.md | ~300 | ~14 KB | Details |
| **TOTAL ADDITIONS** | **~1,390** | **~58 KB** | **Complete Integration** |

---

## 🚀 Next Steps

1. **Now:** Run `python quickstart.py` ✅
2. **Next:** Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) (5 min)
3. **Then:** Try examples from [api_usage_examples.py](w5_engine/api_usage_examples.py)
4. **Finally:** Integrate into your application
5. **Later:** Add caching and monitoring

---

## 🎓 Key Concepts

### Automatic Enrichment
The engine automatically fetches and enriches match data without you needing to call API methods directly.

### Three Agents
Statistical agent (no LLM), Tactical agent (OpenAI), Sentiment agent (Anthropic) - each weighted differently.

### Graceful Degradation
If API fails, the system continues with default values - no crashes.

### Data Extraction
Raw API responses are converted to meaningful features for agent analysis.

---

**Ready to start?** → Run `python quickstart.py`

**Need help?** → Read [SOCCERDATA_API_INTEGRATION.md](SOCCERDATA_API_INTEGRATION.md)

**See examples?** → Check [w5_engine/api_usage_examples.py](w5_engine/api_usage_examples.py)

---

**Integration Complete! 🎉**
