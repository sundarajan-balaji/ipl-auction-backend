from pathlib import Path
from zipfile import ZipFile
import json


DATA_DIR = Path(__file__).resolve().parents[2]

ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"

TARGET_ID = "b4296080"
TARGET_NAME = "Milind Kumar"


with ZipFile(ZIP_FILE, "r") as archive:

    for filename in archive.namelist():

        if not filename.endswith(".json"):
            continue

        with archive.open(filename) as file:
            match = json.load(file)

        info = match.get("info", {})

        registry = (
            info
            .get("registry", {})
            .get("people", {})
        )

        if registry.get(TARGET_NAME) != TARGET_ID:
            continue

        print("=" * 70)
        print("MATCH FOUND")
        print("=" * 70)

        print(f"Match: {filename}")
        print(f"Season: {info.get('season')}")
        print(f"Date: {info.get('dates')}")
        print(f"Teams: {info.get('teams')}")
        print(f"Venue: {info.get('venue')}")

        print("\nPlayer lists:")

        for team, players in info.get("players", {}).items():

            print(f"\n{team}")

            if TARGET_NAME in players:
                print(f"  *** {TARGET_NAME} IS A PLAYER ***")

            for player in players:
                print(f"  {player}")

        print("\nRegistry entry:")
        print(
            TARGET_NAME,
            "->",
            registry.get(TARGET_NAME)
        )

        print("\nOccurrences in deliveries:")

        for innings in match.get("innings", []):

            for over in innings.get("overs", []):

                for delivery in over.get(
                        "deliveries",
                        []
                ):

                    for wicket in delivery.get(
                            "wickets",
                            []
                    ):

                        for fielder in wicket.get(
                                "fielders",
                                []
                        ):

                            if (
                                    fielder.get("name")
                                    == TARGET_NAME
                            ):
                                print(
                                    f"  innings={innings.get('team')} "
                                    f"over={over.get('over')} "
                                    f"delivery={delivery.get('actual_delivery')} "
                                    f"wicket={wicket.get('kind')}"
                                )