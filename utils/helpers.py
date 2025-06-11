def normalize(value, min_val, max_val):
    #normalize value
    return(value - min_val) / (max_val - min_val) if max_val > min_val else 0

def implied_probability(decimal_odds):
    return round(1 / decimal_odds, 4)

def win_probability(team_score, opponent_score):
    total = team_score + opponent_score
    return round(team_score / total, 4) if total > 0 else 0.5

def find_best_lines(game):
    results = {}

    for line_type in ['home_moneyline', 'away_moneyline', 'home_spread', 'away_spread', 'over_under']:
        best_book = None
        best_value = None

        for book, lines in game['odds'].items():
            value = lines.get(line_type)

            #define comp logic based on type
            if 'moneyline' in line_type:
                # best value = closest to 0
                if best_value is None or value > best_value:
                    best_book, best_value = book, value
            elif 'spread' in line_type:
                #for spread, best depends whether its home or away
                if 'home' in line_type:
                    if best_value is None or value > best_value:
                        best_book, best_value = book, value
                else:
                    if best_value is None or value < best_value:
                        best_book, best_value = book, value
            elif line_type == 'over_under':
                if best_value is None or value < best_value:
                    best_book, best_value = book, value

        results[line_type] = {
            'book': best_book,
            'value': best_value
        }
    return results

def calculate_edge(win_probability, market_prob):
    return round(win_probability - market_prob, 4)

def moneyline_to_decimal(ml):
    if ml > 0:
        return round((ml / 100) + 1, 4)
    else:
        return round((100 / abs(ml)) + 1, 4)

def normalize_team_score(value, max_value):
    adjusted = (max_value + 1 - value)
    return adjusted / max_value