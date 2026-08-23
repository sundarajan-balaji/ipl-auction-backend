from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def validate_statistics():

    total_runs = 0
    batter_runs = 0
    extra_runs = 0

    total_deliveries = 0

    total_fours = 0
    total_sixes = 0

    wicket_events = 0
    catches = 0
    stumpings = 0
    run_outs = 0

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = sorted(
            name
            for name in archive.namelist()
            if name.endswith(".json")
        )

        for filename in json_files:

            with archive.open(filename) as file:
                match = json.load(file)

            for innings in match.get("innings", []):

                for over in innings.get("overs", []):

                    for delivery in over.get("deliveries", []):

                        total_deliveries += 1

                        runs = delivery.get("runs", {})
                        extras = delivery.get("extras", {})

                        total_runs += runs.get("total", 0)
                        batter_runs += runs.get("batter", 0)
                        extra_runs += runs.get("extras", 0)

                        if runs.get("batter") == 4:
                            total_fours += 1

                        elif runs.get("batter") == 6:
                            total_sixes += 1

                        for wicket in delivery.get("wickets", []):

                            wicket_events += 1

                            kind = wicket.get("kind")

                            if kind == "caught":
                                catches += 1

                            elif kind == "stumped":
                                stumpings += 1

                            elif kind == "run out":
                                run_outs += 1

    print("=" * 70)
    print("INDEPENDENT STATISTICS VALIDATION")
    print("=" * 70)

    print(f"\nDeliveries: {total_deliveries}")

    print("\nRUNS")
    print(f"  Total runs:    {total_runs}")
    print(f"  Batter runs:   {batter_runs}")
    print(f"  Extra runs:    {extra_runs}")
    print(f"  Batter + extra: {batter_runs + extra_runs}")

    print(
        f"\nRuns reconcile: "
        f"{total_runs == batter_runs + extra_runs}"
    )

    print("\nBOUNDARIES")
    print(f"  Fours: {total_fours}")
    print(f"  Sixes: {total_sixes}")

    print("\nWICKETS")
    print(f"  Total wicket events: {wicket_events}")
    print(f"  Caught: {catches}")
    print(f"  Stumped: {stumpings}")
    print(f"  Run outs: {run_outs}")


if __name__ == "__main__":
    validate_statistics()