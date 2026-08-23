from pathlib import Path
from zipfile import ZipFile
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def inspect_dataset():
    print("=" * 60)
    print("CRICSHEET IPL DATASET INSPECTION")
    print("=" * 60)

    if not ZIP_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {ZIP_FILE}"
        )

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
        ]

        print(f"\nJSON files found: {len(json_files)}")

        if not json_files:
            raise RuntimeError("No JSON files found in archive.")

        print("\nFirst 10 files:")
        for filename in json_files[:10]:
            print(f"  - {filename}")

        # Inspect the first match
        first_match = json_files[0]

        print("\n" + "=" * 60)
        print(f"INSPECTING: {first_match}")
        print("=" * 60)

        with archive.open(first_match) as file:
            match = json.load(file)

        print("\nTop-level keys:")
        for key in match.keys():
            print(f"  - {key}")

        print("\nFull metadata:")
        print(json.dumps(
            {
                key: match[key]
                for key in match.keys()
                if key != "innings"
            },
            indent=2
        ))

        print("\nNumber of innings:")
        print(len(match.get("innings", [])))

        print("\n" + "=" * 60)
        print("FIRST INNINGS INSPECTION")
        print("=" * 60)

        first_innings = match["innings"][0]

        print("\nInnings keys:")
        for key in first_innings.keys():
            print(f"  - {key}")

        print("\nInnings metadata:")
        print(json.dumps(
            {
                key: first_innings[key]
                for key in first_innings
                if key != "overs"
            },
            indent=2
        ))

        overs = first_innings.get("overs", [])

        print(f"\nNumber of overs: {len(overs)}")

        if overs:
            first_over = overs[0]

            print("\nFirst over keys:")
            for key in first_over.keys():
                print(f"  - {key}")

            print("\nFirst over:")
            print(json.dumps(first_over, indent=2))


if __name__ == "__main__":
    inspect_dataset()