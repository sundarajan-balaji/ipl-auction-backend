from pathlib import Path
import csv
from collections import defaultdict


DATA_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
        DATA_DIR
        / "processed"
        / "player_match_stats.csv"
)

OUTPUT_FILE = (
        DATA_DIR
        / "processed"
        / "player_season_stats.csv"
)


def safe_strike_rate(runs, balls):
    if balls == 0:
        return 0.0

    return round(
        (runs / balls) * 100,
        2
    )


def safe_average(runs, dismissals):
    if dismissals == 0:
        return 0.0

    return round(
        runs / dismissals,
        2
    )


def safe_economy(runs_conceded, balls_bowled):
    if balls_bowled == 0:
        return 0.0

    return round(
        (runs_conceded / balls_bowled) * 6,
        2
    )


def build_player_season_stats():

    # ========================================================
    # LOAD MATCH STATS
    # ========================================================

    with open(
            INPUT_FILE,
            "r",
            encoding="utf-8",
            newline=""
    ) as file:

        reader = csv.DictReader(file)

        rows = list(reader)

    # ========================================================
    # AGGREGATION
    # ========================================================

    season_stats = defaultdict(
        lambda: {
            "player_name": "",
            "season": "",

            "matches": 0,

            # Batting
            "batting_innings": 0,
            "runs": 0,
            "balls_faced": 0,
            "fours": 0,
            "sixes": 0,
            "dismissals": 0,

            # Bowling
            "bowling_innings": 0,
            "runs_conceded": 0,
            "balls_bowled": 0,
            "wickets": 0,
            "maidens": 0,

            # Fielding
            "catches": 0,
            "stumpings": 0,
            "run_outs": 0,

            # Internal tracking
            "_matches": set(),
        }
    )

    # ========================================================
    # PROCESS MATCH RECORDS
    # ========================================================

    for row in rows:

        player_id = row[
            "cricsheet_player_id"
        ]

        season = row[
            "season"
        ]

        key = (
            player_id,
            season
        )

        stats = season_stats[key]

        stats["player_name"] = row[
            "player_name"
        ]

        stats["season"] = season

        # ----------------------------------------------------
        # Match participation
        # ----------------------------------------------------

        stats["_matches"].add(
            row["source_match_id"]
        )

        # ----------------------------------------------------
        # Batting
        # ----------------------------------------------------

        stats["batting_innings"] += int(
            row["batting_innings"]
        )

        stats["runs"] += int(
            row["runs"]
        )

        stats["balls_faced"] += int(
            row["balls_faced"]
        )

        stats["fours"] += int(
            row["fours"]
        )

        stats["sixes"] += int(
            row["sixes"]
        )

        stats["dismissals"] += int(
            row["dismissals"]
        )

        # ----------------------------------------------------
        # Bowling
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Fielding
        # ----------------------------------------------------

        stats["catches"] += int(
            row["catches"]
        )

        stats["stumpings"] += int(
            row["stumpings"]
        )

        stats["run_outs"] += int(
            row["run_outs"]
        )

    # ========================================================
    # BUILD OUTPUT
    # ========================================================

    records = []

    for (
            player_id,
            season
    ), stats in sorted(
        season_stats.items(),
        key=lambda item: (
                item[0][1],
                item[1]["player_name"]
        )
    ):

        runs = stats["runs"]

        balls_faced = stats[
            "balls_faced"
        ]

        dismissals = stats[
            "dismissals"
        ]

        runs_conceded = stats[
            "runs_conceded"
        ]

        balls_bowled = stats[
            "balls_bowled"
        ]

        records.append({

            "cricsheet_player_id":
                player_id,

            "player_name":
                stats["player_name"],

            "season":
                season,

            "matches":
                len(stats["_matches"]),

            # ------------------------------------------------
            # Batting
            # ------------------------------------------------

            "batting_innings":
                stats["batting_innings"],

            "runs":
                runs,

            "balls_faced":
                balls_faced,

            "fours":
                stats["fours"],

            "sixes":
                stats["sixes"],

            "dismissals":
                dismissals,

            "strike_rate":
                safe_strike_rate(
                    runs,
                    balls_faced
                ),

            "batting_average":
                safe_average(
                    runs,
                    dismissals
                ),

            # ------------------------------------------------
            # Bowling
            # ------------------------------------------------

            "bowling_innings":
                stats["bowling_innings"],

            "runs_conceded":
                runs_conceded,

            "balls_bowled":
                balls_bowled,

            "wickets":
                stats["wickets"],

            "maidens":
                stats["maidens"],

            "economy":
                safe_economy(
                    runs_conceded,
                    balls_bowled
                ),

            # ------------------------------------------------
            # Fielding
            # ------------------------------------------------

            "catches":
                stats["catches"],

            "stumpings":
                stats["stumpings"],

            "run_outs":
                stats["run_outs"],
        })

    # ========================================================
    # WRITE CSV
    # ========================================================

    fieldnames = [
        "cricsheet_player_id",
        "player_name",
        "season",

        "matches",

        # Batting
        "batting_innings",
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "dismissals",
        "strike_rate",
        "batting_average",

        # Bowling
        "bowling_innings",
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "maidens",
        "economy",

        # Fielding
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

    # ========================================================
    # OUTPUT
    # ========================================================

    print("\n" + "=" * 70)
    print("PLAYER-SEASON STATISTICS GENERATED")
    print("=" * 70)

    print(
        f"Player-season records: "
        f"{len(records)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    build_player_season_stats()