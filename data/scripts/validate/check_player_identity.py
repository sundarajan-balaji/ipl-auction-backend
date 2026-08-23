from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def check_identity():

    # source_id -> set of names
    id_to_names = defaultdict(set)

    # name -> set of source IDs
    name_to_ids = defaultdict(set)

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

            registry = (
                info
                .get("registry", {})
                .get("people", {})
            )

            for team_players in info.get("players", {}).values():

                for player_name in team_players:

                    source_id = registry.get(player_name)

                    if source_id is None:
                        continue

                    id_to_names[source_id].add(player_name)
                    name_to_ids[player_name].add(source_id)

    print("=" * 70)
    print("PLAYER IDENTITY ANALYSIS")
    print("=" * 70)

    print(f"Unique names: {len(name_to_ids)}")
    print(f"Unique IDs:   {len(id_to_names)}")

    print("\n" + "-" * 70)
    print("ONE ID ASSOCIATED WITH MULTIPLE NAMES")
    print("-" * 70)

    found = False

    for source_id, names in sorted(id_to_names.items()):

        if len(names) > 1:

            found = True

            print(f"\n{source_id}")

            for name in sorted(names):
                print(f"  - {name}")

    if not found:
        print("None")

    print("\n" + "-" * 70)
    print("ONE NAME ASSOCIATED WITH MULTIPLE IDS")
    print("-" * 70)

    found = False

    for name, ids in sorted(name_to_ids.items()):

        if len(ids) > 1:

            found = True

            print(f"\n{name}")

            for source_id in sorted(ids):
                print(f"  - {source_id}")

    if not found:
        print("None")


if __name__ == "__main__":
    check_identity()