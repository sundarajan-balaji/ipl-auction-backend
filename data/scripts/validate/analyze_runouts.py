from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def analyze_runouts():

    fielder_counts = Counter()
    examples = []

    total_runouts = 0

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
        ]

        for filename in json_files:

            with archive.open(filename) as file:
                match = json.load(file)

            for innings in match.get("innings", []):

                for over in innings.get("overs", []):

                    for delivery in over.get("deliveries", []):

                        for wicket in delivery.get("wickets", []):

                            if wicket.get("kind") != "run out":
                                continue

                            total_runouts += 1

                            fielders = wicket.get("fielders", [])

                            fielder_count = len(fielders)

                            fielder_counts[fielder_count] += 1

                            if fielder_count > 1 and len(examples) < 20:
                                examples.append({
                                    "match": filename,
                                    "wicket": wicket,
                                    "delivery": delivery
                                })

    print("=" * 70)
    print("RUN-OUT ANALYSIS")
    print("=" * 70)

    print(f"\nTotal run-out events: {total_runouts}")

    print("\nFielders per run-out event:")

    for count, occurrences in sorted(
            fielder_counts.items()
    ):
        print(
            f"  {count} fielder(s): "
            f"{occurrences} events"
        )

    print("\nMultiple-fielder examples:")

    for example in examples:

        print("\nMatch:", example["match"])

        print(
            json.dumps(
                example["wicket"],
                indent=2
            )
        )


if __name__ == "__main__":
    analyze_runouts()