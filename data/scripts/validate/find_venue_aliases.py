from pathlib import Path
import csv
from collections import defaultdict


DATA_DIR = Path(__file__).resolve().parents[2]

MATCHES_FILE = (
        DATA_DIR
        / "processed"
        / "matches.csv"
)


def find_venue_aliases():

    venues = defaultdict(
        lambda: {
            "matches": 0,
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

            venues[venue]["matches"] += 1

            if city:
                venues[venue]["cities"].add(
                    city
                )

    print("=" * 70)
    print("PROBABLE VENUE ALIASES")
    print("=" * 70)

    found = 0

    venue_names = sorted(
        venues.keys()
    )

    for venue in venue_names:

        for other in venue_names:

            if venue == other:
                continue

            # Example:
            #
            # Wankhede Stadium
            # Wankhede Stadium, Mumbai
            #
            if other.startswith(
                    venue + ","
            ):

                found += 1

                print(
                    f"\nPossible canonical : {venue}"
                )

                print(
                    f"Possible alias     : {other}"
                )

                print(
                    f"Canonical matches  : "
                    f"{venues[venue]['matches']}"
                )

                print(
                    f"Alias matches      : "
                    f"{venues[other]['matches']}"
                )

    print(
        f"\nPossible relationships found: "
        f"{found}"
    )


if __name__ == "__main__":
    find_venue_aliases()