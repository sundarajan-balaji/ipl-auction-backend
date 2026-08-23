from pathlib import Path
from zipfile import ZipFile
import csv
import json


DATA_DIR = Path(__file__).resolve().parents[2]

ZIP_FILE = (
        DATA_DIR
        / "raw"
        / "cricsheet"
        / "ipl_json.zip"
)

OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_FILE = OUTPUT_DIR / "matches.csv"


def build_matches():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = []

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = [
            name
            for name in archive.namelist()
            if name.endswith(".json")
        ]

        print(f"Processing {len(json_files)} matches...")

        for index, filename in enumerate(
                sorted(json_files),
                start=1
        ):

            with archive.open(filename) as file:
                match = json.load(file)

            info = match["info"]
            outcome = info.get("outcome", {})
            toss = info.get("toss", {})

            teams = info.get("teams", [])

            # -------------------------------------------------
            # Determine result
            # -------------------------------------------------

            winner = outcome.get("winner")

            result_type = None
            result_margin = None

            if winner:

                by = outcome.get("by", {})

                if "runs" in by:
                    result_type = "WON_BY_RUNS"
                    result_margin = by["runs"]

                elif "wickets" in by:
                    result_type = "WON_BY_WICKETS"
                    result_margin = by["wickets"]

            elif outcome.get("result") == "tie":

                result_type = "TIE"

            elif outcome.get("result") == "no result":

                result_type = "NO_RESULT"

            else:
                raise ValueError(
                    f"Unknown outcome in {filename}: "
                    f"{outcome}"
                )

            # -------------------------------------------------
            # Match record
            # -------------------------------------------------

            records.append({
                "source_match_id": Path(filename).stem,

                "season": str(info.get("season")),

                "match_date": (
                    str(info["dates"][0])
                    if info.get("dates")
                    else None
                ),

                "city": info.get("city"),

                "venue": info.get("venue"),

                "team_1": teams[0] if len(teams) > 0 else None,

                "team_2": teams[1] if len(teams) > 1 else None,

                "toss_winner": toss.get("winner"),

                "toss_decision": toss.get("decision"),

                "winner": winner,

                "result_type": result_type,

                "result_margin": result_margin,

                "player_of_match": (
                    info.get("player_of_match", [None])[0]
                    if info.get("player_of_match")
                    else None
                ),
            })

            if index % 100 == 0:
                print(
                    f"Processed {index}/{len(json_files)} matches"
                )

    # ---------------------------------------------------------
    # Write CSV
    # ---------------------------------------------------------

    fieldnames = [
        "source_match_id",
        "season",
        "match_date",
        "city",
        "venue",
        "team_1",
        "team_2",
        "toss_winner",
        "toss_decision",
        "winner",
        "result_type",
        "result_margin",
        "player_of_match",
    ]

    with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)

    print("\n" + "=" * 60)
    print("MATCH DATASET GENERATED")
    print("=" * 60)

    print(f"Matches: {len(records)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_matches()