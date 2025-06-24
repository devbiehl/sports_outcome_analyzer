# Sports Outcome Analyzer

A Python tool to analyze sports game odds and team stats to estimate win probabilities and betting edges.

## Features

- Supports NFL game analysis.
- Recently added NBA analysis.
- Combines team statistics and sportsbook odds for predictive modeling.
- Calculates implied probabilities and value edges on betting lines.
- Finds best available betting lines from multiple sportsbooks.

## Getting Started

### Prerequisites

- Python 3.x
- requests
- json

### Usage

- Run the main script:
python3 main.py
- Enter the sport you want to analyze(e.g. NFL, NBA).
- Currently using mocked data (will eventually setup API endpoints for each sport added).
- (FOR MOCKED NBA SCHEDULE DATA FILE ONLY) You must change the dates of all games for each team listed for accurate fatigue weighting.
- Currently viewing output in terminal (plan to move to webpage).

### Project Structure 
- main.py: main entry point for running analysis.
- utils/helpers.py: helper functions for calculations and processing data.
- Data files (JSON) currently used as data inputs. Will be moving to live data from APIs.

### Contributing
Feel Free to Fork and submit pull requests with imporvements or new sports support.

### License
MIT License
