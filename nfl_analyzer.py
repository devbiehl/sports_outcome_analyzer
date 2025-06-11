import json
import requests 
from utils.helpers import (
    normalize,
    implied_probability,
    moneyline_to_decimal,
    win_probability,
    find_best_lines,
    calculate_edge,
    normalize_team_score
)

def file_opener(file_name):
    try:
        with open(file_name) as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("FILE NOT FOUND")
        return []

def list_to_dict(list_of_dicts, key_name):
    team_dict = {}
    for dictionary in list_of_dicts:
        key = dictionary[key_name]
        team_dict[key] = dictionary
    return team_dict

def merge_stats_and_odds(odds_data, team_dict):
    #merge team stats to odds by matching home and away to team in stats
    teams_stats_odds = []
    for game in odds_data:
        home = game.get('home_team')
        away = game.get('away_team')
        home_stats = team_dict.get(home, {})
        away_stats = team_dict.get(away, {})
        teams_stats_odds.append({
            'home_team': home,
            'away_team': away,
            'home_stats': home_stats,
            'away_stats': away_stats,
            'odds': game.get('odds')
        })
    return teams_stats_odds

def parse_record(record_str):
    try:
        wins, losses = map(int, record_str.split('-'))
        return wins / (wins + losses) if (wins + losses) > 0 else 0
    except:
        return 0


def analyze_game(game, teams_stats_odds):
    home_stats = game['home_stats']
    away_stats = game['away_stats']
    
    best_lines = find_best_lines(game)

    home_moneyline = best_lines['home_moneyline']['value']
    away_moneyline = best_lines['away_moneyline']['value']

    home_decimal = moneyline_to_decimal(home_moneyline)
    away_decimal = moneyline_to_decimal(away_moneyline)

    home_score = compute_team_score(home_stats)
    away_score = compute_team_score(away_stats)

    home_market_prob = implied_probability(home_decimal)
    away_market_prob = implied_probability(away_decimal)

    home_est_prob = win_probability(home_score, away_score)
    away_est_prob = win_probability(away_score, home_score)

    home_edge = calculate_edge(home_est_prob, home_market_prob)
    away_edge = calculate_edge(away_est_prob, away_market_prob)

    home_chance = round(home_est_prob * 100, 1)
    away_chance = round(away_est_prob * 100, 1)

    return {
        'home_team': game['home_team'],
        'away_team': game['away_team'],
        'home_chance': home_chance,
        'away_chance': away_chance,
        'home_edge': home_edge,
        'away_edge': away_edge,
        'best_lines': best_lines,
        'home_market_chance': home_market_prob,
        'away_market_chance': away_market_prob
    }

def compute_team_score(stats, weights=None):
    weights = weights or {
        'turnover_margin': 0.4,
        'margin_of_victory': 0.25,
        'record_in_one_score_games': 0.15,
        'net_score': 0.2,
    }

    turnover_margin = normalize(stats.get('turnover_margin', 0), -20, 20)
    margin_of_victory = normalize(stats.get('margin_of_victory', 0), -30, 30)
    record_score = parse_record(stats.get('record_in_one_score_games', "0-0"))
    offense_score = normalize_team_score(stats.get('offense_rank', 32), 32)
    defense_score = normalize_team_score(stats.get('defense_rank', 32), 32)
    net_score = (0.6 * offense_score) + (0.4 * defense_score)

    score = (
        weights['turnover_margin'] * turnover_margin +
        weights['margin_of_victory'] * margin_of_victory +
        weights['record_in_one_score_games'] * record_score +
        weights['net_score'] * net_score
    )

    return max(0, min(score, 1))

def run_analysis(teams_stats_odds):
    return [analyze_game(game, teams_stats_odds) for game in teams_stats_odds]


def run_nfl_analysis():
    odds_file = "nfl_odds.json"
    stats_file = "nfl_stats.json"

    odds_data = file_opener(odds_file)
    team_data = file_opener(stats_file)
    team_dict = list_to_dict(team_data, 'team')
    teams_stats_odds = merge_stats_and_odds(odds_data, team_dict)

    results = sorted(run_analysis(teams_stats_odds), key=lambda x: max(x['home_edge'], x['away_edge']), reverse=True)

    for result in results:
        print(f"{result['away_team']} @ {result['home_team']}:")
        print(f"    Market assigned {result['home_team']} win probability: {result['home_market_chance']*100:.1f}%")
        print(f"    Market assigned {result['away_team']} win probability: {result['away_market_chance']*100:.1f}%")
        print(f"    Model est. {result['home_team']} win probability: {result['home_chance']}%")
        print(f"    Model est. {result['away_team']} win probability: {result['away_chance']}%")
        print(f"    {result['home_team']} edge: {result['home_edge']*100:.1f}%")
        print(f"    {result['away_team']} edge: {result['away_edge']*100:.1f}%")
        print(f"    Best Lines:")
        print(f"        Home ML: {result['best_lines']['home_moneyline']['value']} ({result['best_lines']['home_moneyline']['book']})")
        print(f"        Away ML: {result['best_lines']['away_moneyline']['value']} ({result['best_lines']['away_moneyline']['book']})")
        print(f"        Home Spread: {result['best_lines']['home_spread']['value']} ({result['best_lines']['home_spread']['book']})")
        print(f"        Away Spread: {result['best_lines']['away_spread']['value']} ({result['best_lines']['away_spread']['book']})")
        print(f"        Over/Under: {result['best_lines']['over_under']['value']} ({result['best_lines']['over_under']['book']})")
        print(f"-------------------------------------------------")

if __name__ == "__main__":
    run_nfl_analysis()