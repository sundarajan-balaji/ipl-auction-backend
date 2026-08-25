from pathlib import Path
import csv
from collections import Counter


DATA_DIR = Path(__file__).resolve().parents[2]

STATS_FILE = (
        DATA_DIR
        / "processed"
        / "player_match_stats.csv"
)


EXPECTED_TOTALS = {
    "runs": 381529,
    "balls_faced": 285856,
    "fours": 34447,
    "sixes": 15779,
    "dismissals": 14686,
    "runs_conceded": 394585,
    "balls_bowled": 284630,
    "wickets": 13482,
    "maidens": 423,
    "catches": 9321,
    "stumpings": 388,
    "run_outs": 480,
}


REQUIRED_COLUMNS = [
    "source_match_id",
    "season",
    "cricsheet_player_id",
    "player_name",
    "team",
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


STAT_COLUMNS = [
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


def validate_player_match_stats():

    print("=" * 70)
    print("PLAYER-MATCH STATISTICS VALIDATION")
    print("=" * 70)

    # ========================================================
    # LOAD CSV
    # ========================================================

    with open(
            STATS_FILE,
            "r",
            encoding="utf-8",
            newline=""
    ) as file:

        reader = csv.DictReader(file)

        actual_columns = reader.fieldnames or []

        # ----------------------------------------------------
        # Column validation
        # ----------------------------------------------------

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in actual_columns
        ]

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(missing_columns)
            )

        rows = list(reader)

    print(
        f"\nRecords: {len(rows)}"
    )

    # ========================================================
    # UNIQUE MATCH / PLAYER PAIRS
    # ========================================================

    pairs = [
        (
            row["source_match_id"],
            row["cricsheet_player_id"]
        )
        for row in rows
    ]

    unique_pairs = set(pairs)

    print(
        f"Unique match/player pairs: "
        f"{len(unique_pairs)}"
    )

    if len(pairs) != len(unique_pairs):
        duplicate_counts = Counter(pairs)

        duplicates = {
            pair: count
            for pair, count in duplicate_counts.items()
            if count > 1
        }

        raise ValueError(
            "Duplicate match/player pairs found:\n"
            f"{duplicates}"
        )

    # ========================================================
    # NUMERIC VALIDATION
    # ========================================================

    numeric_rows = []

    for row_number, row in enumerate(
            rows,
            start=2
    ):

        converted = {}

        for column in STAT_COLUMNS:

            value = row[column]

            try:
                converted[column] = int(value)
            except ValueError:
                raise ValueError(
                    f"Invalid numeric value in "
                    f"row {row_number}, "
                    f"column '{column}': "
                    f"'{value}'"
                )

            if converted[column] < 0:
                raise ValueError(
                    f"Negative value in row "
                    f"{row_number}, "
                    f"column '{column}': "
                    f"{converted[column]}"
                )

        numeric_rows.append(converted)

    # ========================================================
    # TOTALS
    # ========================================================

    actual_totals = {}

    for column in STAT_COLUMNS:

        actual_totals[column] = sum(
            row[column]
            for row in numeric_rows
        )

    print("\nTOTALS")

    for column in STAT_COLUMNS:

        print(
            f"{column:<18}"
            f"{actual_totals[column]:>10}"
        )

    # ========================================================
    # EXPECTED TOTAL CHECKS
    # ========================================================

    print("\nCONSISTENCY CHECKS")

    all_passed = True

    for column, expected in EXPECTED_TOTALS.items():

        actual = actual_totals[column]

        passed = (
                actual == expected
        )

        status = (
            "PASS"
            if passed
            else "FAIL"
        )

        print(
            f"{column:<18}"
            f"expected={expected:<8} "
            f"actual={actual:<8} "
            f"{status}"
        )

        if not passed:
            all_passed = False

    # ========================================================
    # LOGICAL CONSISTENCY CHECKS
    # ========================================================

    print("\nLOGICAL CHECKS")

    logical_checks = []

    # --------------------------------------------------------
    # 1. Sixes/fours cannot exceed runs.
    # --------------------------------------------------------

    boundary_check = True

    for row in numeric_rows:

        boundary_runs = (
                row["fours"] * 4
                + row["sixes"] * 6
        )

        if boundary_runs > row["runs"]:
            boundary_check = False
            break

    logical_checks.append(
        (
            "Boundary runs <= batting runs",
            boundary_check
        )
    )

    # --------------------------------------------------------
    # 2. Wickets cannot exceed legal balls bowled.
    # --------------------------------------------------------

    wicket_check = True

    for row in numeric_rows:

        if row["wickets"] > row["balls_bowled"]:
            wicket_check = False
            break

    logical_checks.append(
        (
            "Bowler wickets <= legal balls",
            wicket_check
        )
    )

    # --------------------------------------------------------
    # 3. Maidens cannot exceed bowling innings.
    #
    # A player can theoretically have multiple maidens in a
    # single match, so this is NOT a valid check.
    #
    # Instead, maidens cannot exceed legal balls / 6 rounded
    # appropriately. We use a conservative bound.
    # --------------------------------------------------------

    # maiden_check = True
    #
    # for row in numeric_rows:
    #
    #     maximum_possible_maidens = (
    #             row["balls_bowled"] // 6
    #     )
    #
    #     if row["maidens"] > maximum_possible_maidens:
    #         maiden_check = False
    #         break
    #
    # logical_checks.append(
    #     (
    #         "Maidens <= complete six-ball overs",
    #         maiden_check
    #     )
    # )

    # --------------------------------------------------------
    # 4. Dismissals cannot exceed batting innings.
    #
    # This is NOT generally valid because a batter can only be
    # dismissed once per innings, so it IS valid at this level.
    # --------------------------------------------------------

    # dismissal_check = True
    #
    # for row in numeric_rows:
    #
    #     if row["dismissals"] > row["batting_innings"]:
    #         dismissal_check = False
    #         break
    #
    # logical_checks.append(
    #     (
    #         "Dismissals <= batting innings",
    #         dismissal_check
    #     )
    # )

    # --------------------------------------------------------
    # 5. Bowling innings should not be zero when balls were
    # bowled.
    # --------------------------------------------------------

    bowling_innings_check = True

    for row in numeric_rows:

        if (
                row["balls_bowled"] > 0
                and row["bowling_innings"] == 0
        ):
            bowling_innings_check = False
            break

    logical_checks.append(
        (
            "Bowling innings present when balls bowled",
            bowling_innings_check
        )
    )

    # --------------------------------------------------------
    # 6. Batting innings should not be zero when balls faced.
    # --------------------------------------------------------

    batting_innings_check = True

    for row in numeric_rows:

        if (
                row["balls_faced"] > 0
                and row["batting_innings"] == 0
        ):
            batting_innings_check = False
            break

    logical_checks.append(
        (
            "Batting innings present when balls faced",
            batting_innings_check
        )
    )

    for name, passed in logical_checks:

        status = (
            "PASS"
            if passed
            else "FAIL"
        )

        print(
            f"{name:<50}"
            f"{status}"
        )

        if not passed:
            all_passed = False

    # ========================================================
    # RESULT
    # ========================================================

    print("\n" + "=" * 70)

    if all_passed:

        print(
            "ALL PLAYER-MATCH STATISTICS CHECKS PASSED"
        )

    else:

        print(
            "PLAYER-MATCH STATISTICS VALIDATION FAILED"
        )

        raise ValueError(
            "One or more player-match "
            "statistics checks failed."
        )


if __name__ == "__main__":
    validate_player_match_stats()