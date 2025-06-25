from nfl_analyzer import run_nfl_analysis
from nba_analyzer import run_nba_analysis

def main():
    sport = input("Enter sport (NFL, NBA, etc): ").strip().upper()

    if sport == "NFL":
        run_nfl_analysis()
    elif sport == "NBA":
        run_nba_analysis()
    else:
        print(f"{sport} not yet supported.")

if __name__ == "__main__":
    main()