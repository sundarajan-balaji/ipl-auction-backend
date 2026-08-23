from pathlib import Path
from collections import defaultdict
import csv


DATA_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = DATA_DIR / "processed" / "player_match_stats.csv"
OUTPUT_FILE = DATA_DIR / "processed" / "player_season_stats.csv"


def build_player_season_stats():

    aggregations = {}

    with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            player_id = row["cricsheet_player_id"]
            season = row["season"]

            key = (player_id, season)

            if key not in aggregations:

                aggregations[key] = {
                    "cricsheet_player_id": player_id,
                    "player_name": row["player_name"],
                    "season": season,

                    "matches": 0,

                    "batting_innings": 0,
                    "runs": 0,
                    "balls_faced": 0,
                    "fours": 0,
                    "sixes": 0,

                    "bowling_innings": 0,
                    "runs_conceded": 0,
                    "balls_bowled": 0,
                    "wickets": 0,
                    "maidens": 0,

                    "catches": 0,
                    "stumpings": 0,
                    "run_outs": 0,
                }

            stats = aggregations[key]

            stats["matches"] += 1

            stats["batting_innings"] += int(
                row["batting_innings"]
            )

            stats["runs"] += int(row["runs"])
            stats["balls_faced"] += int(
                row["balls_faced"]
            )

            stats["fours"] += int(row["fours"])
            stats["sixes"] += int(row["sixes"])

            stats["bowling_innings"] += int(
                row["bowling_innings"]
            )

            stats["runs_conceded"] += int(
                row["runs_conceded"]
            )

            stats["balls_bowled"] += int(
                row["balls_bowled"]
            )

            stats["wickets"] += int(
                row["wickets"]
            )

            stats["maidens"] += int(
                row["maidens"]
            )

            stats["catches"] += int(
                row["catches"]
            )

            stats["stumpings"] += int(
                row["stumpings"]
            )

            stats["run_outs"] += int(
                row["run_outs"]
            )

    records = []

    for stats in aggregations.values():

        runs = stats["runs"]
        balls_faced = stats["balls_faced"]

        runs_conceded = stats["runs_conceded"]
        balls_bowled = stats["balls_bowled"]

        # -----------------------------------------------------
        # Strike rate
        # -----------------------------------------------------

        if balls_faced > 0:

            strike_rate = (
                                  runs / balls_faced
                          ) * 100

        else:

            strike_rate = 0

        # -----------------------------------------------------
        # Economy
        # -----------------------------------------------------

        if balls_bowled > 0:

            economy = (
                              runs_conceded * 6
                      ) / balls_bowled

        else:

            economy = 0

        # -----------------------------------------------------
        # Batting average
        #
        # We don't yet have dismissals in our statistics
        # table, so we deliberately do NOT calculate it here.
        # -----------------------------------------------------

        records.append({

            "cricsheet_player_id":
                stats["cricsheet_player_id"],

            "player_name":
                stats["player_name"],

            "season":
                stats["season"],

            "matches":
                stats["matches"],

            "batting_innings":
                stats["batting_innings"],

            "runs":
                stats["runs"],

            "balls_faced":
                stats["balls_faced"],

            "fours":
                stats["fours"],

            "sixes":
                stats["sixes"],

            "strike_rate":
                round(strike_rate, 2),

            "bowling_innings":
                stats["bowling_innings"],

            "runs_conceded":
                stats["runs_conceded"],

            "balls_bowled":
                stats["balls_bowled"],

            "wickets":
                stats["wickets"],

            "maidens":
                stats["maidens"],

            "economy":
                round(economy, 2),

            "catches":
                stats["catches"],

            "stumpings":
                stats["stumpings"],

            "run_outs":
                stats["run_outs"],
        })

    records.sort(
        key=lambda row: (
            row["season"],
            row["player_name"]
        )
    )

    fieldnames = [
        "cricsheet_player_id",
        "player_name",
        "season",

        "matches",

        "batting_innings",
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "strike_rate",

        "bowling_innings",
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "maidens",
        "economy",

        "catches",
        "stumpings",
        "run_outs",
    ]

    with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)

    print("\n" + "=" * 70)
    print("PLAYER-SEASON STATISTICS GENERATED")
    print("=" * 70)

    print(
        f"Player-season records: "
        f"{len(records)}"
    )

    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_player_season_stats()