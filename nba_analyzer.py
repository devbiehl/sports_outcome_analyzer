import json
import requests 
from datetime import datetime, timedelta
from utils.helpers import (
    normalize,
    implied_probability,
    moneyline_to_decimal,
    win_probability,
    find_best_lines,
    calculate_edge,
    normalize_team_score
)

def calculate_team_score(stats, weights=None):
    weights = weights or {
        'ortg': 0.225,
        'drtg': 0.2,
        'pace': 0.175,
        'ts%': 0.05,
        'tov%': 0.175,
        'rebound%': 0.175
    }

    ortg_scaled = normalize(stats.get('Ortg'), 100, 130)
    drtg_scaled = normalize(stats.get('Drtg'), 100, 130)
    pace_scaled = normalize(stats.get('Pace'), 95, 105)
    ts_scaled = normalize(stats.get('TS%'), 0.50, 0.65)
    tov_scaled = normalize(stats.get('TOV%'), 10, 20)
    rebound_scaled = normalize(stats.get('Rebound%'), 45, 55)

    team_score = (
        weights['ortg'] * ortg_scaled +
        weights['drtg'] * drtg_scaled +
        weights['pace'] * pace_scaled +
        weights['ts%'] * ts_scaled +
        weights['tov%'] * tov_scaled +
        weights['rebound%'] * rebound_scaled
    )

    return team_score
def merge_data(team_stats, team_odds, team_schedule):
    all_team_data = {}
    for game in team_odds:
        if not isinstance(game, dict):
            print("Bad game data:", game)
            continue
        home = game.get('home_team')
        away = game.get('away_team')
        matchup_id = f"{home}_vs_{away}"
        home_stats = team_stats.get(home, {})
        away_stats = team_stats.get(away, {})
        home_injuries = home_stats.get('injuries', [])
        away_injuries = away_stats.get('injuries', [])
        home_schedule = team_schedule[home]
        away_schedule = team_schedule[away]
        all_team_data[matchup_id] = {
            'home_team': home,
            'away_team': away,
            'home_stats': home_stats,
            'away_stats': away_stats,
            'home_injuries': home_injuries,
            'away_injuries': away_injuries,
            'home_schedule': home_schedule,
            'away_schedule': away_schedule,
            'odds': game.get('odds')
        }
    return all_team_data

def calculate_penalties(schedule, injuries, fatigue_weights, injury_weights):
    if not schedule:
        return {'fatigue': 0, 'injuries': 0, 'total': 0}

    # Convert dates to datetime objects
    for game in schedule:
        game['date'] = datetime.strptime(game['date'], "%Y-%m-%d").date()

    schedule.sort(key=lambda game: game['date'])

    today = datetime.today().date()

    next_game_index = None
    for index, game in enumerate(schedule):
        if game['date'] >= today:
            next_game_index = index
            break
    if next_game_index is None:
        return {'fatigue': 0, 'injuries': 0, 'total': 0}

    current_game = schedule[next_game_index]
    current_game_date = current_game['date']

    current_game['fatigue_score'] = 0

    # Check for back-to-back
    if next_game_index > 0:
        previous_date = schedule[next_game_index - 1]['date']
        if (current_game_date - previous_date) == timedelta(days=1):
            current_game['fatigue_score'] += fatigue_weights['back_to_back']

    #check for 3 games in 4 nights
    games_in_4 = 1
    for j in range(len(schedule)):
        # j also means index
        if j != next_game_index:
            date_diff = abs((schedule[j]['date'] - current_game_date).days)
            if date_diff <= 3:
                games_in_4 += 1
    if games_in_4 >= 3:
        current_game['fatigue_score'] += fatigue_weights['3_games_4_nights']
    # check for long road trip (3+ away games in a row)
    road_streak = 0
    if current_game.get('home_or_away') == 'away':
        road_streak = 1
        # Looking back
        j = next_game_index - 1
        while j >= 0 and schedule[j].get('home_or_away') == 'away':
            road_streak += 1
            j -= 1
        # Looking forward
        j = next_game_index + 1
        while j < len(schedule) and schedule[j].get('home_or_away') == 'away':
            road_streak += 1
            j += 1
        if road_streak >= 3:
            current_game['fatigue_score'] += fatigue_weights['long_road_trip']
    for game in schedule:
        game['date'] = game['date'].strftime("%Y-%m-%d")

    if not injuries:
        current_game['injury_score'] = 0

    current_game['injury_score'] = 0

    if len(injuries) >= 3:
        current_game['injury_score'] += injury_weights['3_max']
    elif len(injuries) == 2:
        current_game['injury_score'] += injury_weights['2_out']
    elif len(injuries) == 1:
        current_game['injury_score'] += injury_weights['1_out']

    return {
        'fatigue': current_game['fatigue_score'], 
        'injuries': current_game['injury_score'],
        'total': current_game['fatigue_score'] + current_game['injury_score']
    }

def all_penalties(all_team_data, fatigue_weights=None, injury_weights=None):
    fatigue_weights = fatigue_weights or {
        'back_to_back': 0.45,
        'long_road_trip': 0.2,
        '3_games_4_nights':0.35,
    }
    injury_weights = injury_weights or {
        '1_out': 0.10,
        '2_out': 0.20,
        '3_max': 0.30
    }
    for matchup_id, matchup in all_team_data.items():
        home_schedule = matchup.get('home_schedule', [])
        away_schedule = matchup.get('away_schedule', [])
        home_injuries = matchup.get('home_injuries', [])
        away_injuries = matchup.get('away_injuries', [])


        matchup['home_penalties'] = calculate_penalties(home_schedule, home_injuries, fatigue_weights, injury_weights)
        matchup['away_penalties'] = calculate_penalties(away_schedule, away_injuries, fatigue_weights, injury_weights)

def file_opener(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"{filename} NOT FOUND")
        return []

def list_to_dict(list_of_dicts, key_name):
    team_dict = {}
    for dictionary in list_of_dicts:
        key = dictionary[key_name]
        team_dict[key] = dictionary
    return team_dict

def run_analysis(all_team_data):
    return [analyze_game(game) for game in all_team_data.values()]

def analyze_game(game):
    home_stats = game['home_stats']
    away_stats = game['away_stats']

    best_lines = find_best_lines(game)

    home_moneyline = best_lines['home_moneyline']['value']
    away_moneyline = best_lines['away_moneyline']['value']

    home_decimal = moneyline_to_decimal(home_moneyline)
    away_decimal = moneyline_to_decimal(away_moneyline)

    home_score = calculate_team_score(home_stats.get('team_stats', {}))
    away_score = calculate_team_score(away_stats.get('team_stats', {}))
    home_penalties = game.get('home_penalties', {}).get('total', 0)
    away_penalties = game.get('away_penalties', {}).get('total', 0)
    
    home_adj_score = home_score * (1 - home_penalties)
    away_adj_score = away_score * (1 - away_penalties)

    home_win_prob = win_probability(home_adj_score, away_adj_score)
    away_win_prob = 1 - home_win_prob

    home_market_prob = implied_probability(home_decimal)
    away_market_prob = implied_probability(away_decimal)

    home_edge = calculate_edge(home_win_prob, home_market_prob)
    away_edge = calculate_edge(away_win_prob, away_market_prob)

    home_chance = round(home_win_prob * 100, 1)
    away_chance = round(away_win_prob * 100, 1)

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

def main():
    team_stats_file = input("Enter Team Stats Filename(JSON format): ")
    schedule_file = input("Enter team schedule FIlename(Json Format): ")
    odds_file = input("Enter matchup odds Filename(Json Format): ")

    team_stats = file_opener(team_stats_file)
    team_schedule = file_opener(schedule_file)
    team_odds = file_opener(odds_file)
    #print("Sample odds data:", team_odds[0])

    all_team_data = merge_data(team_stats, team_odds, team_schedule)

    all_penalties(all_team_data)

    results = sorted(run_analysis(all_team_data), key=lambda x: max(x['home_edge'], x['away_edge']), reverse=True)

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

if __name__ == '__main__':
    main()