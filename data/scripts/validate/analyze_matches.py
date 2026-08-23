from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def analyze_matches():

    outcome_types = Counter()
    win_types = Counter()
    toss_decisions = Counter()

    no_winner_matches = []
    unusual_outcomes = []

    match_dates = Counter()
    match_types = Counter()

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
        ]

        for filename in json_files:

            with archive.open(filename) as file:
                match = json.load(file)

            info = match["info"]
            outcome = info.get("outcome", {})

            # -------------------------------------------------
            # Basic match information
            # -------------------------------------------------

            match_type = info.get("match_type")
            match_types[match_type] += 1

            for date in info.get("dates", []):
                match_dates[str(date)] += 1

            # -------------------------------------------------
            # Toss
            # -------------------------------------------------

            toss = info.get("toss", {})

            decision = toss.get("decision")

            if decision:
                toss_decisions[decision] += 1

            # -------------------------------------------------
            # Outcome
            # -------------------------------------------------

            winner = outcome.get("winner")

            if winner:
                if "by" in outcome:

                    by = outcome["by"]

                    if "runs" in by:
                        outcome_types["win_by_runs"] += 1
                        win_types["runs"] += 1

                    elif "wickets" in by:
                        outcome_types["win_by_wickets"] += 1
                        win_types["wickets"] += 1

                    elif "innings" in by:
                        outcome_types["win_by_innings"] += 1
                        win_types["innings"] += 1

                    else:
                        outcome_types["win_with_unknown_margin"] += 1

                elif "result" in outcome:

                    outcome_types[f"result_{outcome['result']}"] += 1

                else:
                    outcome_types["winner_without_margin"] += 1

            else:

                if "result" in outcome:

                    result = outcome["result"]
                    outcome_types[f"result_{result}"] += 1

                elif "eliminator" in outcome:

                    outcome_types["eliminator"] += 1

                else:

                    outcome_types["no_winner"] += 1

                    no_winner_matches.append({
                        "match": filename,
                        "teams": info.get("teams"),
                        "season": info.get("season"),
                        "date": info.get("dates"),
                        "outcome": outcome
                    })

            # -------------------------------------------------
            # Print unusual outcomes later
            # -------------------------------------------------

            if (
                    "winner" in outcome
                    and "result" in outcome
            ):
                unusual_outcomes.append({
                    "match": filename,
                    "outcome": outcome
                })

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    print("=" * 70)
    print("MATCH DOMAIN ANALYSIS")
    print("=" * 70)

    print("\nMatch types:")
    for value, count in match_types.most_common():
        print(f"  {value}: {count}")

    print("\nToss decisions:")
    for value, count in toss_decisions.most_common():
        print(f"  {value}: {count}")

    print("\nOutcome types:")
    for value, count in outcome_types.most_common():
        print(f"  {value}: {count}")

    print("\nMatches without a winner:")
    print(f"  {len(no_winner_matches)}")

    for match in no_winner_matches[:20]:
        print(f"\n  {match['match']}")
        print(f"    Season : {match['season']}")
        print(f"    Date   : {match['date']}")
        print(f"    Teams  : {match['teams']}")
        print(f"    Outcome: {match['outcome']}")

    print("\nUnusual outcomes:")
    print(f"  {len(unusual_outcomes)}")

    for match in unusual_outcomes[:20]:
        print(f"\n  {match['match']}")
        print(f"    Outcome: {match['outcome']}")


if __name__ == "__main__":
    analyze_matches()