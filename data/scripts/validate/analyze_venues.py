from pathlib import Path
import csv
from collections import defaultdict


DATA_DIR = Path(__file__).resolve().parents[2]

MATCHES_FILE = (
        DATA_DIR
        / "processed"
        / "matches.csv"
)


def analyze_venues():

    venues = defaultdict(
        lambda: {
            "matches": 0,
            "seasons": set(),
            "cities": set(),
        }
    )

    with open(
            MATCHES_FILE,
            "r",
            encoding="utf-8",
            newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            venue = row["venue"].strip()
            city = row["city"].strip()
            season = row["season"]

            venues[venue]["matches"] += 1
            venues[venue]["seasons"].add(season)

            if city:
                venues[venue]["cities"].add(city)

    print("=" * 70)
    print("IPL VENUE ANALYSIS")
    print("=" * 70)

    print(
        f"\nUnique raw venues: {len(venues)}"
    )

    print("\nVENUES")
    print("-" * 70)

    for venue, data in sorted(
            venues.items(),
            key=lambda item: (
                    -item[1]["matches"],
                    item[0]
            )
    ):

        cities = ", ".join(
            sorted(data["cities"])
        )

        seasons = ", ".join(
            sorted(data["seasons"])
        )

        print(
            f"\n{venue}"
        )

        print(
            f"  Matches : {data['matches']}"
        )

        print(
            f"  Cities  : {cities}"
        )

        print(
            f"  Seasons : {seasons}"
        )


if __name__ == "__main__":
    analyze_venues()