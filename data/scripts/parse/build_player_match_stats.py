from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict
import csv
import json


DATA_DIR = Path(__file__).resolve().parents[2]

ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"
OUTPUT_DIR = DATA_DIR / "processed"

PLAYERS_FILE = OUTPUT_DIR / "players.csv"

OUTPUT_FILE = OUTPUT_DIR / "player_match_stats.csv"
VALIDATION_FILE = OUTPUT_DIR / "statistics_validation.txt"


def load_canonical_player_names():
    """
    Load the canonical Cricsheet player ID -> player name mapping.

    players.csv is our authoritative player identity dataset.
    This prevents an incomplete or inconsistent name appearing
    in a particular match from propagating into the statistics.
    """

    player_names = {}

    with open(
            PLAYERS_FILE,
            "r",
            encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            player_id = row["cricsheet_player_id"]
            player_name = row["name"].strip()

            if not player_name:
                raise ValueError(
                    f"Blank player name in players.csv "
                    f"for ID: {player_id}"
                )

            if player_id in player_names:
                raise ValueError(
                    f"Duplicate player ID in players.csv: "
                    f"{player_id}"
                )

            player_names[player_id] = player_name

    print(
        f"Loaded {len(player_names)} canonical players."
    )

    return player_names


def create_stat():
    return {
        # Identity / participation
        "team": None,
        "batting_innings": 0,
        "bowling_innings": 0,

        # Batting
        "runs": 0,
        "balls_faced": 0,
        "fours": 0,
        "sixes": 0,

        # Bowling
        "runs_conceded": 0,
        "balls_bowled": 0,
        "wickets": 0,
        "maidens": 0,

        # Fielding
        "catches": 0,
        "stumpings": 0,
        "run_outs": 0,
    }


def is_legal_delivery(delivery):
    """
    A wide and a no-ball are illegal deliveries.

    They therefore do not count as legal balls bowled.

    A no-ball can still count as a ball faced by the batter.
    A wide does not.
    """

    extras = delivery.get("extras", {})

    return (
            "wides" not in extras
            and "noballs" not in extras
    )


def get_bowler_runs_conceded(delivery):
    """
    Calculate the number of runs charged to the bowler.

    Byes, leg-byes and penalty runs are not charged
    to the bowler.
    """

    runs = delivery.get("runs", {})
    extras = delivery.get("extras", {})

    total_runs = runs.get("total", 0)

    return (
            total_runs
            - extras.get("byes", 0)
            - extras.get("legbyes", 0)
            - extras.get("penalty", 0)
    )


def calculate_batting(delivery, stats, player_ids):
    batter_name = delivery["batter"]

    batter_id = player_ids.get(batter_name)

    if batter_id is None:
        raise ValueError(
            f"No Cricsheet ID found for batter: "
            f"{batter_name}"
        )

    player = stats[batter_id]

    runs = delivery.get("runs", {})
    extras = delivery.get("extras", {})

    player["runs"] += runs.get("batter", 0)

    # A wide does not count as a ball faced.
    if "wides" not in extras:
        player["balls_faced"] += 1

    batter_runs = runs.get("batter", 0)

    if batter_runs == 4:
        player["fours"] += 1

    elif batter_runs == 6:
        player["sixes"] += 1


def calculate_bowling(delivery, stats, player_ids):
    bowler_name = delivery["bowler"]

    bowler_id = player_ids.get(bowler_name)

    if bowler_id is None:
        raise ValueError(
            f"No Cricsheet ID found for bowler: "
            f"{bowler_name}"
        )

    player = stats[bowler_id]

    if is_legal_delivery(delivery):
        player["balls_bowled"] += 1

    player["runs_conceded"] += get_bowler_runs_conceded(
        delivery
    )

    for wicket in delivery.get("wickets", []):

        kind = wicket.get("kind")

        # These dismissals are not credited to the bowler.
        if kind in {
            "run out",
            "retired hurt",
            "retired out",
            "obstructing the field",
        }:
            continue

        player["wickets"] += 1


def calculate_fielding(delivery, stats, player_ids):
    for wicket in delivery.get("wickets", []):

        kind = wicket.get("kind")
        fielders = wicket.get("fielders", [])

        # -----------------------------------------------------
        # Catches
        # -----------------------------------------------------

        if kind == "caught":

            for fielder in fielders:

                name = fielder.get("name")
                player_id = player_ids.get(name)

                if player_id is None:
                    continue

                stats[player_id]["catches"] += 1

        # -----------------------------------------------------
        # Stumpings
        # -----------------------------------------------------

        elif kind == "stumped":

            for fielder in fielders:

                name = fielder.get("name")
                player_id = player_ids.get(name)

                if player_id is None:
                    continue

                stats[player_id]["stumpings"] += 1

        # -----------------------------------------------------
        # Run outs
        # -----------------------------------------------------

        elif kind == "run out":

            # Only attribute a run-out when exactly one
            # fielder is identified.
            #
            # Multiple-fielders remain intentionally
            # unambiguous/unattributed.

            if len(fielders) != 1:
                continue

            name = fielders[0].get("name")
            player_id = player_ids.get(name)

            if player_id is None:
                continue

            stats[player_id]["run_outs"] += 1


def calculate_maiden(over, stats, player_ids):
    """
    Award a maiden only when a single bowler delivers
    all six legal balls of an over and concedes zero runs.

    Interrupted/mixed-bowler overs do not produce a maiden.
    """

    deliveries = over.get("deliveries", [])

    if not deliveries:
        return

    bowler_data = defaultdict(
        lambda: {
            "legal_balls": 0,
            "runs": 0,
        }
    )

    for delivery in deliveries:

        bowler_name = delivery["bowler"]
        bowler_id = player_ids.get(bowler_name)

        if bowler_id is None:
            raise ValueError(
                f"No Cricsheet ID found for bowler: "
                f"{bowler_name}"
            )

        bowler_data[bowler_id]["runs"] += (
            get_bowler_runs_conceded(delivery)
        )

        if is_legal_delivery(delivery):
            bowler_data[bowler_id]["legal_balls"] += 1

    # A standard maiden requires one bowler to deliver
    # all six legal balls and concede zero runs.
    for bowler_id, data in bowler_data.items():

        if (
                data["legal_balls"] == 6
                and data["runs"] == 0
        ):
            stats[bowler_id]["maidens"] += 1


def build_player_match_stats():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Load canonical player identities
    # ---------------------------------------------------------

    canonical_player_names = (
        load_canonical_player_names()
    )

    records = []

    total_batting_runs = 0
    total_balls_faced = 0

    total_bowling_runs = 0
    total_balls_bowled = 0
    total_wickets = 0
    total_maidens = 0

    total_catches = 0
    total_stumpings = 0
    total_run_outs = 0

    with ZipFile(ZIP_FILE, "r") as archive:

        json_files = sorted(
            name
            for name in archive.namelist()
            if name.endswith(".json")
        )

        print(
            f"Processing {len(json_files)} matches..."
        )

        for index, filename in enumerate(
                json_files,
                start=1
        ):

            with archive.open(filename) as file:
                match = json.load(file)

            info = match["info"]

            match_id = Path(filename).stem
            season = str(info.get("season"))

            # -------------------------------------------------
            # Build name -> Cricsheet ID mapping for this match
            # -------------------------------------------------

            registry = (
                info
                .get("registry", {})
                .get("people", {})
            )

            # -------------------------------------------------
            # Match-level team mapping
            # -------------------------------------------------

            teams = info.get("teams", [])

            # -------------------------------------------------
            # Player statistics for this match
            # -------------------------------------------------

            stats = defaultdict(create_stat)

            # -------------------------------------------------
            # Process innings
            # -------------------------------------------------

            for innings in match.get("innings", []):

                batting_team = innings["team"]

                # -------------------------------------------------
                # Determine fielding team
                # -------------------------------------------------

                fielding_team = next(
                    (
                        team
                        for team in teams
                        if team != batting_team
                    ),
                    None
                )

                innings_batters = set()
                innings_bowlers = set()

                for over in innings.get("overs", []):

                    calculate_maiden(
                        over,
                        stats,
                        registry
                    )

                    for delivery in over.get(
                            "deliveries",
                            []
                    ):

                        batter_name = delivery["batter"]
                        bowler_name = delivery["bowler"]

                        batter_id = registry.get(
                            batter_name
                        )

                        bowler_id = registry.get(
                            bowler_name
                        )

                        if batter_id is None:
                            raise ValueError(
                                f"Missing registry ID for "
                                f"batter {batter_name} "
                                f"in {filename}"
                            )

                        if bowler_id is None:
                            raise ValueError(
                                f"Missing registry ID for "
                                f"bowler {bowler_name} "
                                f"in {filename}"
                            )

                        # -------------------------------------------------
                        # Verify canonical identity exists
                        # -------------------------------------------------

                        if batter_id not in canonical_player_names:
                            raise ValueError(
                                f"Batter ID {batter_id} "
                                f"({batter_name}) is missing "
                                f"from players.csv"
                            )

                        if bowler_id not in canonical_player_names:
                            raise ValueError(
                                f"Bowler ID {bowler_id} "
                                f"({bowler_name}) is missing "
                                f"from players.csv"
                            )

                        # -----------------------------------------
                        # Batting
                        # -----------------------------------------

                        calculate_batting(
                            delivery,
                            stats,
                            registry
                        )

                        player = stats[batter_id]

                        player["team"] = batting_team

                        innings_batters.add(
                            batter_id
                        )

                        # -----------------------------------------
                        # Bowling
                        # -----------------------------------------

                        calculate_bowling(
                            delivery,
                            stats,
                            registry
                        )

                        bowler = stats[bowler_id]

                        bowler["team"] = fielding_team

                        innings_bowlers.add(
                            bowler_id
                        )

                        # -----------------------------------------
                        # Fielding
                        # -----------------------------------------

                        calculate_fielding(
                            delivery,
                            stats,
                            registry
                        )

                        # Fielders belong to the fielding team.
                        for wicket in delivery.get(
                                "wickets",
                                []
                        ):

                            for fielder in wicket.get(
                                    "fielders",
                                    []
                            ):

                                name = fielder.get("name")

                                player_id = registry.get(
                                    name
                                )

                                if player_id is None:
                                    continue

                                if player_id not in canonical_player_names:
                                    raise ValueError(
                                        f"Fielder ID {player_id} "
                                        f"({name}) is missing "
                                        f"from players.csv"
                                    )

                                stats[player_id]["team"] = (
                                    fielding_team
                                )

                # ---------------------------------------------
                # Mark innings participation
                # ---------------------------------------------

                for player_id in innings_batters:
                    stats[player_id]["batting_innings"] += 1

                for player_id in innings_bowlers:
                    stats[player_id]["bowling_innings"] += 1

            # -------------------------------------------------
            # Generate player-match records
            # -------------------------------------------------

            for player_id, player in stats.items():

                # Every player appearing in a statistic must
                # have a canonical identity.
                if player_id not in canonical_player_names:
                    raise ValueError(
                        f"Player ID {player_id} "
                        f"has no canonical identity"
                    )

                records.append({
                    "source_match_id": match_id,
                    "season": season,

                    "cricsheet_player_id": player_id,

                    # IMPORTANT:
                    # Always use the canonical name from
                    # players.csv.
                    "player_name":
                        canonical_player_names[player_id],

                    "team": player["team"],

                    "batting_innings":
                        player["batting_innings"],

                    "runs":
                        player["runs"],

                    "balls_faced":
                        player["balls_faced"],

                    "fours":
                        player["fours"],

                    "sixes":
                        player["sixes"],

                    "bowling_innings":
                        player["bowling_innings"],

                    "runs_conceded":
                        player["runs_conceded"],

                    "balls_bowled":
                        player["balls_bowled"],

                    "wickets":
                        player["wickets"],

                    "maidens":
                        player["maidens"],

                    "catches":
                        player["catches"],

                    "stumpings":
                        player["stumpings"],

                    "run_outs":
                        player["run_outs"],
                })

                # -------------------------------------------------
                # Validation totals
                # -------------------------------------------------

                total_batting_runs += player["runs"]
                total_balls_faced += player["balls_faced"]

                total_bowling_runs += player[
                    "runs_conceded"
                ]

                total_balls_bowled += player[
                    "balls_bowled"
                ]

                total_wickets += player["wickets"]
                total_maidens += player["maidens"]

                total_catches += player["catches"]
                total_stumpings += player["stumpings"]
                total_run_outs += player["run_outs"]

            if index % 100 == 0:
                print(
                    f"Processed "
                    f"{index}/{len(json_files)} matches"
                )

    # ---------------------------------------------------------
    # Write CSV
    # ---------------------------------------------------------

    fieldnames = [
        "source_match_id",
        "season",

        "cricsheet_player_id",
        "player_name",
        "team",

        "batting_innings",
        "runs",
        "balls_faced",
        "fours",
        "sixes",

        "bowling_innings",
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "maidens",

        "catches",
        "stumpings",
        "run_outs",
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

    # ---------------------------------------------------------
    # Validation report
    # ---------------------------------------------------------

    with open(
            VALIDATION_FILE,
            "w",
            encoding="utf-8"
    ) as file:

        file.write(
            "IPL STATISTICS VALIDATION\n"
        )

        file.write(
            "=========================\n\n"
        )

        file.write(
            f"Matches processed: "
            f"{len(json_files)}\n"
        )

        file.write(
            f"Player-match records: "
            f"{len(records)}\n"
        )

        file.write(
            f"Total batting runs: "
            f"{total_batting_runs}\n"
        )

        file.write(
            f"Total balls faced: "
            f"{total_balls_faced}\n"
        )

        file.write(
            f"Total bowling runs conceded: "
            f"{total_bowling_runs}\n"
        )

        file.write(
            f"Total legal balls bowled: "
            f"{total_balls_bowled}\n"
        )

        file.write(
            f"Total bowling wickets credited: "
            f"{total_wickets}\n"
        )

        file.write(
            f"Total maidens: "
            f"{total_maidens}\n"
        )

        file.write(
            f"Total catches: "
            f"{total_catches}\n"
        )

        file.write(
            f"Total stumpings: "
            f"{total_stumpings}\n"
        )

        file.write(
            f"Unambiguously attributed run outs: "
            f"{total_run_outs}\n"
        )

    # ---------------------------------------------------------
    # Console summary
    # ---------------------------------------------------------

    print("\n" + "=" * 70)
    print("PLAYER-MATCH STATISTICS GENERATED")
    print("=" * 70)

    print(
        f"Matches processed: "
        f"{len(json_files)}"
    )

    print(
        f"Player-match records: "
        f"{len(records)}"
    )

    print(
        f"Total batting runs: "
        f"{total_batting_runs}"
    )

    print(
        f"Total balls faced: "
        f"{total_balls_faced}"
    )

    print(
        f"Total bowling runs conceded: "
        f"{total_bowling_runs}"
    )

    print(
        f"Total legal balls bowled: "
        f"{total_balls_bowled}"
    )

    print(
        f"Bowler wickets credited: "
        f"{total_wickets}"
    )

    print(
        f"Total maidens: "
        f"{total_maidens}"
    )

    print(
        f"Total catches: "
        f"{total_catches}"
    )

    print(
        f"Total stumpings: "
        f"{total_stumpings}"
    )

    print(
        f"Unambiguous run outs: "
        f"{total_run_outs}"
    )

    print(f"\nOutput:")
    print(OUTPUT_FILE)

    print(f"\nValidation:")
    print(VALIDATION_FILE)


if __name__ == "__main__":
    build_player_match_stats()