from pathlib import Path
from collections import defaultdict
import csv


DATA_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = DATA_DIR / "processed" / "player_match_stats.csv"


def validate_player_match_stats():

    totals = defaultdict(int)

    records = 0

    unique_match_player_pairs = set()

    with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            records += 1

            match_id = row["source_match_id"]
            player_id = row["cricsheet_player_id"]

            pair = (match_id, player_id)

            if pair in unique_match_player_pairs:
                raise ValueError(
                    f"Duplicate player-match record: "
                    f"{match_id} / {player_id}"
                )

            unique_match_player_pairs.add(pair)

            totals["runs"] += int(row["runs"])
            totals["balls_faced"] += int(
                row["balls_faced"]
            )

            totals["fours"] += int(row["fours"])
            totals["sixes"] += int(row["sixes"])

            totals["runs_conceded"] += int(
                row["runs_conceded"]
            )

            totals["balls_bowled"] += int(
                row["balls_bowled"]
            )

            totals["wickets"] += int(
                row["wickets"]
            )

            totals["maidens"] += int(
                row["maidens"]
            )

            totals["catches"] += int(
                row["catches"]
            )

            totals["stumpings"] += int(
                row["stumpings"]
            )

            totals["run_outs"] += int(
                row["run_outs"]
            )

    print("=" * 70)
    print("PLAYER-MATCH STATISTICS VALIDATION")
    print("=" * 70)

    print(f"\nRecords: {records}")
    print(
        f"Unique match/player pairs: "
        f"{len(unique_match_player_pairs)}"
    )

    print("\nTOTALS")
    print(f"Runs:             {totals['runs']}")
    print(f"Balls faced:      {totals['balls_faced']}")
    print(f"Fours:            {totals['fours']}")
    print(f"Sixes:            {totals['sixes']}")

    print(
        f"Runs conceded:    "
        f"{totals['runs_conceded']}"
    )

    print(
        f"Legal balls:      "
        f"{totals['balls_bowled']}"
    )

    print(
        f"Wickets:          "
        f"{totals['wickets']}"
    )

    print(
        f"Maidens:          "
        f"{totals['maidens']}"
    )

    print(
        f"Catches:          "
        f"{totals['catches']}"
    )

    print(
        f"Stumpings:        "
        f"{totals['stumpings']}"
    )

    print(
        f"Run-out credits:  "
        f"{totals['run_outs']}"
    )

    print("\nCONSISTENCY CHECKS")

    expected = {
        "runs": 381529,
        "balls_faced": 285856,
        "fours": 34447,
        "sixes": 15779,
        "runs_conceded": 394585,
        "balls_bowled": 284630,
        "wickets": 13482,
        "maidens": 361,
        "catches": 9321,
        "stumpings": 388,
        "run_outs": 480,
    }

    all_passed = True

    for key, expected_value in expected.items():

        actual_value = totals[key]

        passed = actual_value == expected_value

        status = "PASS" if passed else "FAIL"

        print(
            f"{key:18} "
            f"expected={expected_value:<8} "
            f"actual={actual_value:<8} "
            f"{status}"
        )

        if not passed:
            all_passed = False

    print("\n" + "=" * 70)

    if all_passed:
        print("ALL PLAYER-MATCH STATISTICS CHECKS PASSED")
    else:
        print("PLAYER-MATCH STATISTICS VALIDATION FAILED")
        raise SystemExit(1)


if __name__ == "__main__":
    validate_player_match_stats()