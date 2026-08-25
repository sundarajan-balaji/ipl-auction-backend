from pathlib import Path
import csv
from collections import defaultdict, Counter


DATA_DIR = Path(__file__).resolve().parents[2]

MATCH_STATS_FILE = (
        DATA_DIR
        / "processed"
        / "player_match_stats.csv"
)

SEASON_STATS_FILE = (
        DATA_DIR
        / "processed"
        / "player_season_stats.csv"
)


# ============================================================
# HELPERS
# ============================================================

def calculate_strike_rate(runs, balls):
    if balls == 0:
        return 0.0

    return round(
        (runs / balls) * 100,
        2
    )


def calculate_batting_average(runs, dismissals):
    if dismissals == 0:
        return 0.0

    return round(
        runs / dismissals,
        2
    )


def calculate_economy(runs_conceded, balls_bowled):
    if balls_bowled == 0:
        return 0.0

    return round(
        (runs_conceded / balls_bowled) * 6,
        2
    )


# ============================================================
# MAIN
# ============================================================

def validate_player_season_stats():

    print("=" * 70)
    print("PLAYER-SEASON STATISTICS VALIDATION")
    print("=" * 70)

    # ========================================================
    # LOAD MATCH-LEVEL DATA
    # ========================================================

    with open(
            MATCH_STATS_FILE,
            "r",
            encoding="utf-8",
            newline=""
    ) as file:

        match_reader = csv.DictReader(file)

        match_rows = list(match_reader)

    print(
        f"\nMatch-level records: "
        f"{len(match_rows)}"
    )

    # ========================================================
    # LOAD SEASON-LEVEL DATA
    # ========================================================

    with open(
            SEASON_STATS_FILE,
            "r",
            encoding="utf-8",
            newline=""
    ) as file:

        season_reader = csv.DictReader(file)

        season_rows = list(season_reader)

    print(
        f"Season-level records: "
        f"{len(season_rows)}"
    )

    # ========================================================
    # REQUIRED SEASON COLUMNS
    # ========================================================

    required_columns = [
        "cricsheet_player_id",
        "player_name",
        "season",
        "matches",

        "batting_innings",
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "dismissals",
        "strike_rate",
        "batting_average",

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

    missing_columns = [
        column
        for column in required_columns
        if column not in season_reader.fieldnames
    ]

    if missing_columns:
        raise ValueError(
            "Missing columns in player-season stats: "
            + ", ".join(missing_columns)
        )

    # ========================================================
    # AGGREGATE MATCH-LEVEL DATA
    #
    # Key:
    #
    #     (player_id, season)
    #
    # ========================================================

    aggregated = defaultdict(
        lambda: {
            "player_name": "",
            "matches": set(),

            "batting_innings": 0,
            "runs": 0,
            "balls_faced": 0,
            "fours": 0,
            "sixes": 0,
            "dismissals": 0,

            "bowling_innings": 0,
            "runs_conceded": 0,
            "balls_bowled": 0,
            "wickets": 0,
            "maidens": 0,

            "catches": 0,
            "stumpings": 0,
            "run_outs": 0,
        }
    )

    for row in match_rows:

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

        stats = aggregated[key]

        stats["player_name"] = row[
            "player_name"
        ]

        stats["matches"].add(
            row["source_match_id"]
        )

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

    # ========================================================
    # UNIQUE SEASON KEYS
    # ========================================================

    season_keys = [
        (
            row["cricsheet_player_id"],
            row["season"]
        )
        for row in season_rows
    ]

    unique_season_keys = set(
        season_keys
    )

    print(
        f"Unique player-season pairs: "
        f"{len(unique_season_keys)}"
    )

    if len(season_keys) != len(
            unique_season_keys
    ):

        duplicates = {
            key: count
            for key, count in Counter(
                season_keys
            ).items()
            if count > 1
        }

        raise ValueError(
            "Duplicate player-season pairs found:\n"
            f"{duplicates}"
        )

    # ========================================================
    # RECORD COUNT
    # ========================================================

    print("\nRECORD COUNT")

    record_count_pass = (
            len(aggregated)
            == len(season_rows)
    )

    print(
        f"Match-derived player-season pairs: "
        f"{len(aggregated)}"
    )

    print(
        f"CSV player-season records:          "
        f"{len(season_rows)}"
    )

    print(
        f"Record count: "
        f"{'PASS' if record_count_pass else 'FAIL'}"
    )

    # ========================================================
    # CONVERT SEASON CSV INTO LOOKUP
    # ========================================================

    season_lookup = {}

    for row in season_rows:

        key = (
            row["cricsheet_player_id"],
            row["season"]
        )

        season_lookup[key] = row

    # ========================================================
    # AGGREGATE TOTALS
    # ========================================================

    stat_columns = [
        "batting_innings",
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "dismissals",

        "bowling_innings",
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "maidens",

        "catches",
        "stumpings",
        "run_outs",
    ]

    print("\nAGGREGATE TOTALS")

    all_passed = record_count_pass

    for column in stat_columns:

        match_total = sum(
            stats[column]
            for stats in aggregated.values()
        )

        season_total = sum(
            int(row[column])
            for row in season_rows
        )

        passed = (
                match_total == season_total
        )

        print(
            f"{column:<18}"
            f"match={match_total:<8} "
            f"season={season_total:<8} "
            f"{'PASS' if passed else 'FAIL'}"
        )

        if not passed:
            all_passed = False

    # ========================================================
    # PLAYER-SEASON RECORD VALIDATION
    # ========================================================

    print("\nPLAYER-SEASON RECORD CHECKS")

    record_failures = []

    for key, expected in aggregated.items():

        actual = season_lookup.get(key)

        if actual is None:

            record_failures.append(
                f"Missing season record: {key}"
            )

            continue

        # ----------------------------------------------------
        # Identity
        # ----------------------------------------------------

        if actual["player_name"] != expected[
            "player_name"
        ]:

            record_failures.append(
                f"Name mismatch: {key} | "
                f"expected={expected['player_name']} "
                f"actual={actual['player_name']}"
            )

        # ----------------------------------------------------
        # Matches
        # ----------------------------------------------------

        expected_matches = len(
            expected["matches"]
        )

        actual_matches = int(
            actual["matches"]
        )

        if expected_matches != actual_matches:

            record_failures.append(
                f"Match count mismatch: {key} | "
                f"expected={expected_matches} "
                f"actual={actual_matches}"
            )

        # ----------------------------------------------------
        # Integer statistics
        # ----------------------------------------------------

        for column in stat_columns:

            expected_value = expected[
                column
            ]

            actual_value = int(
                actual[column]
            )

            if expected_value != actual_value:

                record_failures.append(
                    f"{column} mismatch: {key} | "
                    f"expected={expected_value} "
                    f"actual={actual_value}"
                )

        # ----------------------------------------------------
        # Strike rate
        # ----------------------------------------------------

        expected_strike_rate = (
            calculate_strike_rate(
                expected["runs"],
                expected["balls_faced"]
            )
        )

        actual_strike_rate = float(
            actual["strike_rate"]
        )

        if (
                expected_strike_rate
                != actual_strike_rate
        ):

            record_failures.append(
                f"Strike rate mismatch: {key} | "
                f"expected={expected_strike_rate} "
                f"actual={actual_strike_rate}"
            )

        # ----------------------------------------------------
        # Batting average
        # ----------------------------------------------------

        expected_average = (
            calculate_batting_average(
                expected["runs"],
                expected["dismissals"]
            )
        )

        actual_average = float(
            actual["batting_average"]
        )

        if (
                expected_average
                != actual_average
        ):

            record_failures.append(
                f"Batting average mismatch: {key} | "
                f"expected={expected_average} "
                f"actual={actual_average}"
            )

        # ----------------------------------------------------
        # Economy
        # ----------------------------------------------------

        expected_economy = (
            calculate_economy(
                expected["runs_conceded"],
                expected["balls_bowled"]
            )
        )

        actual_economy = float(
            actual["economy"]
        )

        if (
                expected_economy
                != actual_economy
        ):

            record_failures.append(
                f"Economy mismatch: {key} | "
                f"expected={expected_economy} "
                f"actual={actual_economy}"
            )

    if record_failures:

        print(
            f"FAIL — {len(record_failures)} "
            f"record-level problems found."
        )

        for failure in record_failures[:20]:
            print(
                f"  {failure}"
            )

        if len(record_failures) > 20:

            print(
                f"  ... and "
                f"{len(record_failures) - 20} "
                f"more"
            )

        all_passed = False

    else:

        print(
            "All player-season records: PASS"
        )

    # ========================================================
    # CHECK FOR EXTRA RECORDS
    # ========================================================

    extra_keys = (
            unique_season_keys
            - set(aggregated.keys())
    )

    if extra_keys:

        print(
            f"Extra player-season records: "
            f"{len(extra_keys)}"
        )

        for key in list(extra_keys)[:20]:

            print(
                f"  {key}"
            )

        all_passed = False

    else:

        print(
            "No extra player-season records: PASS"
        )

    # ========================================================
    # RESULT
    # ========================================================

    print("\n" + "=" * 70)

    if all_passed:

        print(
            "ALL PLAYER-SEASON STATISTICS "
            "CHECKS PASSED"
        )

    else:

        print(
            "PLAYER-SEASON STATISTICS "
            "VALIDATION FAILED"
        )

        raise ValueError(
            "One or more player-season "
            "statistics checks failed."
        )


if __name__ == "__main__":
    validate_player_season_stats()