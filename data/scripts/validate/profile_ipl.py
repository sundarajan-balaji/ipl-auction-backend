from pathlib import Path
from zipfile import ZipFile
from collections import Counter, defaultdict
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def profile_dataset():

    print("=" * 70)
    print("CRICSHEET IPL DATASET PROFILE")
    print("=" * 70)

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
        ]

        seasons = Counter()
        teams = Counter()
        players = {}
        venues = Counter()
        cities = Counter()
        wicket_types = Counter()
        extras_types = Counter()
        delivery_count = 0
        innings_count = 0
        player_of_match = Counter()

        for index, filename in enumerate(json_files, start=1):

            with archive.open(filename) as file:
                match = json.load(file)

            info = match["info"]

            # -------------------------
            # Match-level information
            # -------------------------

            season = info.get("season")
            seasons[season] += 1

            for team in info.get("teams", []):
                teams[team] += 1

            venue = info.get("venue")
            if venue:
                venues[venue] += 1

            city = info.get("city")
            if city:
                cities[city] += 1

            for player in info.get("player_of_match", []):
                player_of_match[player] += 1

            registry = (
                info
                .get("registry", {})
                .get("people", {})
            )

            players.update(registry)

            # -------------------------
            # Innings / delivery data
            # -------------------------

            innings = match.get("innings", [])

            innings_count += len(innings)

            for innings_data in innings:

                for over in innings_data.get("overs", []):

                    for delivery in over.get("deliveries", []):

                        delivery_count += 1

                        extras = delivery.get("extras", {})

                        for extra_type in extras:
                            extras_types[extra_type] += 1

                        for wicket in delivery.get("wickets", []):

                            wicket_type = wicket.get("kind")

                            if wicket_type:
                                wicket_types[wicket_type] += 1

            if index % 100 == 0:
                print(f"Processed {index}/{len(json_files)} matches")

    # -------------------------
    # Print results
    # -------------------------

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nMatches: {len(json_files)}")
    print(f"Innings: {innings_count}")
    print(f"Deliveries: {delivery_count}")
    print(f"Unique players: {len(players)}")
    print(f"Unique teams: {len(teams)}")
    print(f"Unique venues: {len(venues)}")
    print(f"Unique cities: {len(cities)}")

    print("\n" + "-" * 70)
    print("SEASONS")
    print("-" * 70)

    for season, count in sorted(seasons.items(), key=lambda item: str(item[0])):
        print(f"{season}: {count} matches")

    print("\n" + "-" * 70)
    print("TEAMS")
    print("-" * 70)

    for team, count in teams.most_common():
        print(f"{team}: {count} matches")

    print("\n" + "-" * 70)
    print("EXTRAS")
    print("-" * 70)

    for extra, count in extras_types.most_common():
        print(f"{extra}: {count}")

    print("\n" + "-" * 70)
    print("WICKET TYPES")
    print("-" * 70)

    for wicket, count in wicket_types.most_common():
        print(f"{wicket}: {count}")

    print("\n" + "-" * 70)
    print("TOP PLAYER OF MATCH")
    print("-" * 70)

    for player, count in player_of_match.most_common(20):
        print(f"{player}: {count}")

    print("\n" + "-" * 70)
    print("TOP VENUES")
    print("-" * 70)

    for venue, count in venues.most_common(20):
        print(f"{venue}: {count}")


if __name__ == "__main__":
    profile_dataset()