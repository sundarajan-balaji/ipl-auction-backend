from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def analyze_events():

    wicket_examples = {}
    extra_examples = {}

    player_names = set()
    registry_players = set()

    wicket_count = 0
    extra_count = 0

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

            # Players explicitly associated with each team
            for team_players in info.get("players", {}).values():
                player_names.update(team_players)

            # Registry
            registry = (
                info
                .get("registry", {})
                .get("people", {})
            )

            registry_players.update(registry.keys())

            # Events
            for innings in match.get("innings", []):

                for over in innings.get("overs", []):

                    for delivery in over.get("deliveries", []):

                        extras = delivery.get("extras", {})

                        for extra_type in extras:
                            extra_count += 1

                            if extra_type not in extra_examples:
                                extra_examples[extra_type] = delivery

                        wickets = delivery.get("wickets", [])

                        for wicket in wickets:

                            wicket_count += 1

                            kind = wicket.get("kind")

                            if kind not in wicket_examples:
                                wicket_examples[kind] = wicket

    print("=" * 70)
    print("PLAYER ANALYSIS")
    print("=" * 70)

    print(f"Players from info.players : {len(player_names)}")
    print(f"People in registry        : {len(registry_players)}")

    print(
        f"Registry-only people      : "
        f"{len(registry_players - player_names)}"
    )

    print("\nRegistry-only examples:")

    for name in sorted(registry_players - player_names)[:30]:
        print(f"  {name}")

    print("\n" + "=" * 70)
    print("WICKET ANALYSIS")
    print("=" * 70)

    print(f"Total wickets: {wicket_count}")

    for kind, example in wicket_examples.items():

        print(f"\n{kind}:")
        print(json.dumps(example, indent=2))

    print("\n" + "=" * 70)
    print("EXTRA ANALYSIS")
    print("=" * 70)

    print(f"Total deliveries containing extras: {extra_count}")

    for extra_type, example in extra_examples.items():

        print(f"\n{extra_type}:")
        print(json.dumps(example, indent=2))


if __name__ == "__main__":
    analyze_events()