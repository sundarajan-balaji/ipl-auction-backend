from pathlib import Path
from zipfile import ZipFile
import json


DATA_DIR = Path(__file__).resolve().parents[2]
ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"


def bowler_runs(delivery):
    runs = delivery.get("runs", {})
    extras = delivery.get("extras", {})

    return (
            runs.get("total", 0)
            - extras.get("byes", 0)
            - extras.get("legbyes", 0)
            - extras.get("penalty", 0)
    )


def is_legal(delivery):
    extras = delivery.get("extras", {})

    return (
            "wides" not in extras
            and "noballs" not in extras
    )


def validate_overs():

    mixed_overs = []

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = sorted(
            name
            for name in archive.namelist()
            if name.endswith(".json")
        )

        for filename in json_files:

            with archive.open(filename) as file:
                match = json.load(file)

            for innings in match.get("innings", []):

                for over in innings.get("overs", []):

                    deliveries = over.get("deliveries", [])

                    bowlers = {
                        delivery["bowler"]
                        for delivery in deliveries
                    }

                    if len(bowlers) <= 1:
                        continue

                    # -----------------------------------------
                    # Analyse each bowler's portion
                    # -----------------------------------------

                    bowler_stats = {}

                    for delivery in deliveries:

                        bowler = delivery["bowler"]

                        if bowler not in bowler_stats:
                            bowler_stats[bowler] = {
                                "deliveries": 0,
                                "legal_balls": 0,
                                "runs": 0
                            }

                        stats = bowler_stats[bowler]

                        stats["deliveries"] += 1
                        stats["runs"] += bowler_runs(
                            delivery
                        )

                        if is_legal(delivery):
                            stats["legal_balls"] += 1

                    mixed_overs.append({
                        "match": filename,
                        "over": over.get("over"),
                        "bowlers": bowler_stats
                    })

    print("=" * 70)
    print("MIXED-BOWLER OVER ANALYSIS")
    print("=" * 70)

    print(
        f"\nMixed-bowler overs: "
        f"{len(mixed_overs)}"
    )

    for item in mixed_overs[:20]:

        print(
            f"\n{item['match']} | "
            f"over {item['over']}"
        )

        for bowler, stats in item["bowlers"].items():

            print(
                f"  {bowler}: "
                f"{stats['deliveries']} deliveries, "
                f"{stats['legal_balls']} legal, "
                f"{stats['runs']} runs conceded"
            )


if __name__ == "__main__":
    validate_overs()