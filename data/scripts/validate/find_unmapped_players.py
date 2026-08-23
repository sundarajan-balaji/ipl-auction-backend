from pathlib import Path
from zipfile import ZipFile
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def find_unmapped_players():

    unmapped = []

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

            for team, players in info.get("players", {}).items():

                for player in players:

                    if player not in registry:

                        unmapped.append({
                            "match": filename,
                            "team": team,
                            "player": player,
                            "season": info.get("season")
                        })

    print("=" * 70)
    print("UNMAPPED PLAYERS")
    print("=" * 70)

    print(f"Total occurrences: {len(unmapped)}")

    for item in unmapped:
        print(
            f"{item['player']} | "
            f"{item['team']} | "
            f"{item['season']} | "
            f"{item['match']}"
        )


if __name__ == "__main__":
    find_unmapped_players()