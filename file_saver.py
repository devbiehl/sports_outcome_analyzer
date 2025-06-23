import json

#paste data
data = {
  "Pacers": [
    {"date": "2025-06-08", "opponent": "Celtics", "home_or_away": "away", "result": "L", "back_to_back": false, "game_in_trip": 1, "days_rest": 2},
    {"date": "2025-06-10", "opponent": "76ers", "home_or_away": "away", "result": "W", "back_to_back": false, "game_in_trip": 2, "days_rest": 1},
    {"date": "2025-06-11", "opponent": "Thunder", "home_or_away": "home", "result": null, "back_to_back": true, "game_in_trip": 1, "days_rest": 0}
  ],
  "Thunder": [
    {"date": "2025-06-07", "opponent": "Spurs", "home_or_away": "home", "result": "W", "back_to_back": false, "game_in_trip": 1, "days_rest": 3},
    {"date": "2025-06-10", "opponent": "Bulls", "home_or_away": "away", "result": "L", "back_to_back": false, "game_in_trip": 1, "days_rest": 2},
    {"date": "2025-06-11", "opponent": "Pacers", "home_or_away": "away", "result": null, "back_to_back": true, "game_in_trip": 2, "days_rest": 0}
  ],
  "Knicks": [
    {"date": "2025-06-08", "opponent": "Nets", "home_or_away": "home", "result": "W", "back_to_back": false, "game_in_trip": 1, "days_rest": 2},
    {"date": "2025-06-10", "opponent": "Heat", "home_or_away": "away", "result": "L", "back_to_back": false, "game_in_trip": 1, "days_rest": 1},
    {"date": "2025-06-11", "opponent": "Warriors", "home_or_away": "home", "result": null, "back_to_back": true, "game_in_trip": 1, "days_rest": 0}
  ],
  "Warriors": [
    {"date": "2025-06-07", "opponent": "Kings", "home_or_away": "home", "result": "L", "back_to_back": false, "game_in_trip": 1, "days_rest": 3},
    {"date": "2025-06-09", "opponent": "Raptors", "home_or_away": "away", "result": "W", "back_to_back": false, "game_in_trip": 1, "days_rest": 1},
    {"date": "2025-06-11", "opponent": "Knicks", "home_or_away": "away", "result": null, "back_to_back": true, "game_in_trip": 2, "days_rest": 1}
  ]
}








def file_writer(file_output):
    with open(file_output, 'w') as file:
        json.dump(data, file, indent=4)
    print("File Saved")

file_output = input("Enter desired file name (add format e.g. .json):  ")

save_file = file_writer(file_output)