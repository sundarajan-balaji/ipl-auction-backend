from pathlib import Path
from zipfile import ZipFile
from collections import Counter
import json


DATA_DIR = Path(__file__).resolve().parents[2]

ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


DISMISSAL_TYPES = {
    "caught",
    "bowled",
    "lbw",
    "caught and bowled",
    "stumped",
    "hit wicket",
    "run out",
    "retired out",
    "obstructing the field",
}


def validate_dismissals():

    dismissal_counts = Counter()

    total_dismissals = 0
    retired_hurt = 0

    with ZipFile(ZIP_FILE, "r") as archive:

        for filename in archive.namelist():

            if not filename.endswith(".json"):
                continue

            with archive.open(filename) as file:
                match = json.load(file)

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

                            kind = wicket.get("kind")

                            if kind == "retired hurt":
                                retired_hurt += 1

                            if kind in DISMISSAL_TYPES:

                                total_dismissals += 1
                                dismissal_counts[kind] += 1

    print("=" * 70)
    print("DISMISSAL VALIDATION")
    print("=" * 70)

    print(
        f"\nTotal batting dismissals: "
        f"{total_dismissals}"
    )

    print(
        f"Retired hurt events: "
        f"{retired_hurt}"
    )

    print("\nDISMISSAL TYPES")

    for kind, count in sorted(
            dismissal_counts.items()
    ):
        print(
            f"{kind}: {count}"
        )


if __name__ == "__main__":
    validate_dismissals()