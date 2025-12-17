from typing import Dict, List, Any
from .agents import LLMAgent
from .soccerdata_client import SoccerdataClient
import numpy as np

class ConsensusEngine:
    def __init__(self, debate_rounds: int = 2, min_agents: int = 3):
        self.debate_rounds = debate_rounds
        self.soccerdata = SoccerdataClient()
        self.agents = [
            # Statistician: Uses hard data logic (Soccerdata API)
            LLMAgent('statistician', provider='deterministic'),
            
            # Tactician: OpenAI
            LLMAgent('tactician', provider='openai', model_name='gpt-4o-mini'),
            
            # Sentiment: Anthropic
            LLMAgent('sentiment_analyst', provider='anthropic', model_name='claude-3-haiku-20240307')
        ]

    def run_consensus(self, match_data: Dict[str, Any], baseline_prediction=None) -> Dict[str, Any]:
        print(f"🤖 Starting Debate for {match_data.get('home_team')}...")
        
        # Match data should already be enriched by the loader, but enrich further if needed
        # by adding IDs if they're passed in
        if 'home_team_id' in match_data and 'away_team_id' in match_data and 'league_id' in match_data:
            enriched_data = self._enrich_with_api_stats(match_data)
        else:
            # Data is already enriched, just use it
            enriched_data = match_data
        
        results = []
        for agent in self.agents:
            res = agent.analyze(enriched_data)
            res['agent'] = agent.persona
            results.append(res)
            
            # SAFE PRINTING (Prevents 500 Error)
            hw = res.get('home_win')
            hw_str = f"{hw:.0%}" if hw is not None else "N/A"
            print(f"   👤 {agent.persona}: Home {hw_str} | {res.get('reasoning')}")

        # Weighted Average
        weights = {"statistician": 1.5, "tactician": 1.0, "sentiment_analyst": 0.8}
        final_pred = self._calculate_weighted_average(results, weights)
        
        return {
            "consensus_prediction": final_pred,
            "confidence": 0.5,
            "agreement_score": 0.5,
            "debate_summary": "Debate complete.",
            "agent_analyses": results,
            "api_enrichment": enriched_data.get('api_stats', {})
        }

    def _calculate_weighted_average(self, results, weights):
        h, d, a, tot = 0, 0, 0, 0
        for res in results:
            w = weights.get(res['agent'], 1.0)
            # Default to 0.33 if None to prevent crash
            h += (res.get('home_win') or 0.33) * w
            d += (res.get('draw') or 0.33) * w
            a += (res.get('away_win') or 0.33) * w
            tot += w
        
        if tot == 0: return {"home_win": 0.33, "draw": 0.34, "away_win": 0.33}
        
        # Calculate weighted averages
        h_avg = round(h / tot, 2)
        d_avg = round(d / tot, 2)
        a_avg = round(a / tot, 2)
        
        # Ensure probabilities sum to exactly 1.0 by adjusting the smallest value
        total = h_avg + d_avg + a_avg
        if abs(total - 1.0) > 0.01:
            # Adjust away_win to ensure sum equals 1.0
            a_avg = round(1.0 - h_avg - d_avg, 2)
        
        return {
            "home_win": h_avg,
            "draw": d_avg,
            "away_win": a_avg
        }
    
    # ... (Keep agreement/summary methods if needed)
    def _calculate_agreement(self, results):
        return 0.5 # Simplified for stability
    
    def _enrich_with_api_stats(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich match data with Soccerdata API statistics
        Includes: standings, head-to-head, transfers, team info
        """
        api_stats = {
            'league_standing': None,
            'head_to_head': None,
            'home_team_transfers': None,
            'away_team_transfers': None,
            'home_stadium': None,
            'away_stadium': None,
            'match_preview': None,
            'recent_matches': None
        }
        
        try:
            # Extract IDs from match_data
            league_id = match_data.get('league_id')
            home_team_id = match_data.get('home_team_id')
            away_team_id = match_data.get('away_team_id')
            match_id = match_data.get('match_id')
            
            # Fetch league standing
            if league_id:
                standing = self.soccerdata.get_standing(league_id)
                api_stats['league_standing'] = standing
                print(f"   📊 League standing fetched for league {league_id}")
            
            # Fetch head-to-head stats
            if home_team_id and away_team_id:
                h2h = self.soccerdata.get_head_to_head(home_team_id, away_team_id)
                api_stats['head_to_head'] = h2h
                if h2h:
                    h2h_summary = self.soccerdata.extract_h2h_stats(home_team_id, away_team_id)
                    print(f"   🔄 H2H: {h2h_summary['team1_name']} {h2h_summary['team1_wins']}W-{h2h_summary['draws']}D-{h2h_summary['team2_wins']}W vs {h2h_summary['team2_name']}")
            
            # Fetch team transfers
            if home_team_id:
                home_transfers = self.soccerdata.get_transfers(home_team_id)
                api_stats['home_team_transfers'] = home_transfers
            
            if away_team_id:
                away_transfers = self.soccerdata.get_transfers(away_team_id)
                api_stats['away_team_transfers'] = away_transfers
            
            # Fetch stadiums
            if home_team_id:
                home_stadium = self.soccerdata.get_stadium(team_id=home_team_id)
                api_stats['home_stadium'] = home_stadium
            
            if away_team_id:
                away_stadium = self.soccerdata.get_stadium(team_id=away_team_id)
                api_stats['away_stadium'] = away_stadium
            
            # Fetch match preview (if match_id available)
            if match_id:
                preview = self.soccerdata.get_match_preview(match_id)
                api_stats['match_preview'] = preview
                if preview and preview.get('match_data', {}).get('prediction'):
                    print(f"   🎯 Match Preview: {preview['match_data']['prediction']['choice']}")
            
            # Fetch recent matches
            if league_id:
                recent = self.soccerdata.get_matches(league_id=league_id)
                api_stats['recent_matches'] = recent
            
        except Exception as e:
            print(f"   ⚠️ API enrichment error: {str(e)}")
        
        # Add enriched data to match_data
        enriched_data = match_data.copy()
        enriched_data['api_stats'] = api_stats
        
        # Convert API stats to quantitative features for agents
        enriched_data['quantitative_features'] = self._extract_quantitative_features(api_stats)
        enriched_data['qualitative_context'] = self._extract_qualitative_context(api_stats)
        
        return enriched_data
    
    def _extract_quantitative_features(self, api_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Extract numerical features from API stats for agent analysis"""
        features = {}
        
        # Extract from head-to-head
        if api_stats.get('head_to_head'):
            h2h_summary = self.soccerdata.extract_h2h_stats(
                api_stats['head_to_head'].get('team1', {}).get('id', 0),
                api_stats['head_to_head'].get('team2', {}).get('id', 0)
            )
            if h2h_summary:
                features['h2h_overall_games'] = h2h_summary['overall_games']
                features['h2h_team1_wins'] = h2h_summary['team1_wins']
                features['h2h_team2_wins'] = h2h_summary['team2_wins']
                features['h2h_draws'] = h2h_summary['draws']
                features['h2h_team1_win_pct'] = h2h_summary['team1_win_percentage']
                features['h2h_team1_home_wins'] = h2h_summary['team1_home_wins']
        
        # Extract from standing
        if api_stats.get('league_standing'):
            standing = api_stats['league_standing']
            if standing.get('stage'):
                for stage in standing['stage']:
                    standings_list = stage.get('standings', [])
                    if standings_list:
                        features['league_teams_count'] = len(standings_list)
                        top_team = standings_list[0]
                        features['league_leader_points'] = top_team.get('points')
        
        return features
    
    def _extract_qualitative_context(self, api_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Extract qualitative context from API stats"""
        context = {}
        
        # Extract preview insights
        if api_stats.get('match_preview'):
            preview = api_stats['match_preview']
            context['weather'] = preview.get('match_data', {}).get('weather')
            context['excitement_rating'] = preview.get('match_data', {}).get('excitement_rating')
            context['ai_prediction'] = preview.get('match_data', {}).get('prediction', {}).get('choice')
        
        # Extract transfer context
        if api_stats.get('home_team_transfers'):
            transfers_in = api_stats['home_team_transfers'].get('transfers', {}).get('transfers_in', [])
            transfers_out = api_stats['home_team_transfers'].get('transfers', {}).get('transfers_out', [])
            context['home_recent_signings'] = len(transfers_in[:3])  # Last 3 signings
            context['home_recent_departures'] = len(transfers_out[:3])
        
        return context