from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict
import csv
import json


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path(__file__).resolve().parents[2]

ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"

PROCESSED_DIR = DATA_DIR / "processed"

PLAYERS_FILE = PROCESSED_DIR / "players.csv"

OUTPUT_FILE = PROCESSED_DIR / "player_match_stats.csv"

VALIDATION_FILE = PROCESSED_DIR / "statistics_validation.txt"


# ============================================================
# WICKET DEFINITIONS
# ============================================================

# Wicket types that count as a batting dismissal.
#
# "retired hurt" is intentionally excluded.
#
# This gives us:
#
# 14,686 batting dismissals
# 19 retired hurt events
# 14,705 total wicket events
#
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


# Wicket types credited to the bowler.
#
# Run-outs, retired outs, obstructing the field and retired hurt
# are NOT credited to the bowler.
#
BOWLER_WICKET_TYPES = {
    "bowled",
    "caught",
    "lbw",
    "caught and bowled",
    "stumped",
    "hit wicket",
}


# ============================================================
# STAT STRUCTURE
# ============================================================

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
        "dismissals": 0,

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


# ============================================================
# HELPERS
# ============================================================

def is_legal_delivery(delivery):
    """
    A delivery is legal if it is not a wide or no-ball.

    Wides and no-balls do not count towards the bowler's
    six legal deliveries in an over.
    """

    extras = delivery.get("extras", {})

    return (
            "wides" not in extras
            and "noballs" not in extras
    )


def calculate_batting(
        delivery,
        stats,
        player_ids,
):
    """
    Calculate batter statistics for one delivery.
    """

    batter_name = delivery.get("batter")

    if not batter_name:
        return

    player_id = player_ids.get(batter_name)

    if player_id is None:
        raise ValueError(
            f"No Cricsheet ID found for batter "
            f"'{batter_name}'"
        )

    player = stats[player_id]

    player["runs"] += delivery.get(
        "runs",
        {}
    ).get(
        "batter",
        0
    )

    # --------------------------------------------------------
    # Balls faced
    #
    # Wides are not balls faced.
    #
    # No-balls are generally counted as balls faced in
    # this dataset's historical statistical treatment only
    # when the batter actually receives the delivery.
    #
    # For standard IPL statistics, no-balls count as balls
    # faced unless the delivery is a wide.
    # --------------------------------------------------------

    extras = delivery.get("extras", {})

    if "wides" not in extras:
        player["balls_faced"] += 1

    batter_runs = delivery.get(
        "runs",
        {}
    ).get(
        "batter",
        0
    )

    if batter_runs == 4:
        player["fours"] += 1

    elif batter_runs == 6:
        player["sixes"] += 1


def calculate_bowling(
        delivery,
        stats,
        player_ids,
):
    """
    Calculate bowling statistics for one delivery.
    """

    bowler_name = delivery.get("bowler")

    if not bowler_name:
        return

    player_id = player_ids.get(bowler_name)

    if player_id is None:
        raise ValueError(
            f"No Cricsheet ID found for bowler "
            f"'{bowler_name}'"
        )

    player = stats[player_id]

    extras = delivery.get(
        "extras",
        {}
    )

    runs = delivery.get(
        "runs",
        {}
    )

    # --------------------------------------------------------
    # Bowling runs conceded
    #
    # Bowler does NOT get charged for:
    #
    # - byes
    # - leg byes
    # - penalty runs
    #
    # Batter runs + wides + no-balls are charged.
    # --------------------------------------------------------

    bowler_runs = runs.get(
        "batter",
        0
    )

    bowler_runs += extras.get(
        "wides",
        0
    )

    bowler_runs += extras.get(
        "noballs",
        0
    )

    player["runs_conceded"] += bowler_runs

    # --------------------------------------------------------
    # Legal delivery
    # --------------------------------------------------------

    if is_legal_delivery(delivery):
        player["balls_bowled"] += 1

    # --------------------------------------------------------
    # Wickets credited to bowler
    # --------------------------------------------------------

    for wicket in delivery.get(
            "wickets",
            []
    ):

        kind = wicket.get("kind")

        if kind in BOWLER_WICKET_TYPES:
            player["wickets"] += 1


def calculate_dismissal(
        delivery,
        stats,
        player_ids,
        batting_team,
):
    """
    Count batting dismissals.

    Retired hurt is deliberately excluded.

    The dismissed player belongs to the batting team
    for the innings.
    """

    for wicket in delivery.get(
            "wickets",
            []
    ):

        kind = wicket.get("kind")

        if kind not in DISMISSAL_TYPES:
            continue

        player_out = wicket.get(
            "player_out"
        )

        if not player_out:
            continue

        player_id = player_ids.get(
            player_out
        )

        if player_id is None:
            raise ValueError(
                f"No Cricsheet ID found for dismissed "
                f"player '{player_out}'"
            )

        stats[player_id][
            "dismissals"
        ] += 1

        stats[player_id][
            "team"
        ] = batting_team


def calculate_fielding(
        delivery,
        stats,
        player_ids,
        fielding_team,
):
    """
    Calculate catches, stumpings and unambiguous run-outs.

    Also assigns the player's team to the fielding team.

    Important:

    A substitute fielder may appear in Cricsheet's
    delivery data without appearing in info.players.

    Because build_players.py now discovers such players,
    their Cricsheet IDs are valid canonical IDs.
    """

    for wicket in delivery.get(
            "wickets",
            []
    ):

        kind = wicket.get(
            "kind"
        )

        fielders = wicket.get(
            "fielders",
            []
        )

        # ----------------------------------------------------
        # Catches
        # ----------------------------------------------------

        if kind == "caught":

            for fielder in fielders:

                name = fielder.get(
                    "name"
                )

                if not name:
                    continue

                player_id = player_ids.get(
                    name
                )

                if player_id is None:
                    raise ValueError(
                        f"No Cricsheet ID found for "
                        f"fielder '{name}'"
                    )

                stats[player_id][
                    "catches"
                ] += 1

                stats[player_id][
                    "team"
                ] = fielding_team

        # ----------------------------------------------------
        # Stumpings
        # ----------------------------------------------------

        elif kind == "stumped":

            for fielder in fielders:

                name = fielder.get(
                    "name"
                )

                if not name:
                    continue

                player_id = player_ids.get(
                    name
                )

                if player_id is None:
                    raise ValueError(
                        f"No Cricsheet ID found for "
                        f"fielder '{name}'"
                    )

                stats[player_id][
                    "stumpings"
                ] += 1

                stats[player_id][
                    "team"
                ] = fielding_team

        # ----------------------------------------------------
        # Run outs
        #
        # Only assign when exactly one fielder is supplied.
        #
        # If multiple fielders are supplied, we cannot
        # unambiguously decide who gets the run-out credit.
        # ----------------------------------------------------

        elif kind == "run out":

            if len(fielders) != 1:
                continue

            name = fielders[0].get(
                "name"
            )

            if not name:
                continue

            player_id = player_ids.get(
                name
            )

            if player_id is None:
                raise ValueError(
                    f"No Cricsheet ID found for "
                    f"fielder '{name}'"
                )

            stats[player_id][
                "run_outs"
            ] += 1

            stats[player_id][
                "team"
            ] = fielding_team


def calculate_maiden_overs(
        overs,
        stats,
        player_ids,
):
    """
    Calculate maiden overs.

    A maiden is credited only when:

    1. The entire over was bowled by exactly one bowler.
    2. That bowler is identified in the canonical player map.
    3. The bowler conceded zero runs during the entire over.

    Mixed-bowler overs are deliberately excluded.
    """

    # --------------------------------------------------------
    # Find all bowlers who participated in this over.
    # --------------------------------------------------------

    bowlers = set()

    for delivery in overs:

        bowler_name = delivery.get("bowler")

        if not bowler_name:
            continue

        player_id = player_ids.get(
            bowler_name
        )

        if player_id is None:
            raise ValueError(
                f"No Cricsheet ID found for bowler "
                f"'{bowler_name}'"
            )

        bowlers.add(player_id)

    # --------------------------------------------------------
    # A normal maiden must belong to exactly one bowler.
    #
    # Mixed-bowler overs are therefore excluded.
    # --------------------------------------------------------

    if len(bowlers) != 1:
        return

    bowler_id = next(iter(bowlers))

    # --------------------------------------------------------
    # Calculate the total runs conceded by that bowler
    # during the entire over.
    # --------------------------------------------------------

    total_runs_conceded = 0

    for delivery in overs:

        extras = delivery.get(
            "extras",
            {}
        )

        runs = delivery.get(
            "runs",
            {}
        )

        # Batter runs are charged to bowler.
        total_runs_conceded += runs.get(
            "batter",
            0
        )

        # Wides are charged to bowler.
        total_runs_conceded += extras.get(
            "wides",
            0
        )

        # No-balls are charged to bowler.
        total_runs_conceded += extras.get(
            "noballs",
            0
        )

        # Byes, leg-byes and penalty runs are deliberately
        # not charged to the bowler.

    # --------------------------------------------------------
    # Zero runs conceded = maiden.
    # --------------------------------------------------------

    if total_runs_conceded == 0:

        stats[bowler_id][
            "maidens"
        ] += 1


# ============================================================
# MAIN BUILDER
# ============================================================

def build_player_match_stats():

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load canonical players
    #
    # IMPORTANT:
    #
    # Use canonical_player_names because that is the mapping
    # generated by the current data pipeline.
    #
    # player_id -> player_name
    # --------------------------------------------------------

    canonical_player_names = {}

    with open(
            PLAYERS_FILE,
            "r",
            encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            player_id = row[
                "cricsheet_player_id"
            ]

            player_name = row[
                "name"
            ]

            canonical_player_names[
                player_id
            ] = player_name

    print(
        f"Loaded "
        f"{len(canonical_player_names)} "
        f"canonical players."
    )

    # --------------------------------------------------------
    # Output records
    # --------------------------------------------------------

    records = []

    # --------------------------------------------------------
    # Global validation totals
    # --------------------------------------------------------

    total_matches = 0
    total_player_match_records = 0

    total_batting_runs = 0
    total_balls_faced = 0
    total_fours = 0
    total_sixes = 0
    total_dismissals = 0

    total_bowling_runs = 0
    total_legal_balls = 0
    total_bowler_wickets = 0
    total_maidens = 0

    total_catches = 0
    total_stumpings = 0
    total_run_outs = 0

    # --------------------------------------------------------
    # Process ZIP
    # --------------------------------------------------------

    with ZipFile(
            ZIP_FILE,
            "r"
    ) as archive:

        json_files = sorted(
            name
            for name in archive.namelist()
            if name.endswith(".json")
        )

        print(
            f"Processing "
            f"{len(json_files)} matches..."
        )

        for index, filename in enumerate(
                json_files,
                start=1
        ):

            with archive.open(
                    filename
            ) as file:

                match = json.load(file)

            total_matches += 1

            info = match.get(
                "info",
                {}
            )

            season = str(
                info.get(
                    "season"
                )
            )

            # ------------------------------------------------
            # Registry
            #
            # name -> Cricsheet ID
            # ------------------------------------------------

            registry = (
                info
                .get("registry", {})
                .get("people", {})
            )

            player_ids = registry

            # ------------------------------------------------
            # Match ID
            # ------------------------------------------------

            match_id = filename.rsplit(
                ".",
                1
            )[0]

            # ------------------------------------------------
            # Player stats
            #
            # player_id -> stats
            # ------------------------------------------------

            stats = defaultdict(
                create_stat
            )

            # ------------------------------------------------
            # Process innings
            # ------------------------------------------------

            for innings in match.get(
                    "innings",
                    []
            ):

                batting_team = innings.get(
                    "team"
                )

                # ------------------------------------------------
                # Determine fielding team
                # ------------------------------------------------

                fielding_team = next(
                    (
                        team
                        for team in info.get(
                        "teams",
                        []
                    )
                        if team != batting_team
                    ),
                    None
                )

                innings_batters = set()
                innings_bowlers = set()

                overs = innings.get(
                    "overs",
                    []
                )

                # ------------------------------------------------
                # Process each over
                # ------------------------------------------------

                for over in overs:

                    deliveries = over.get(
                        "deliveries",
                        []
                    )

                    # ------------------------------------------------
                    # Calculate maiden status for the over
                    #
                    # We do this before processing individual
                    # delivery statistics.
                    # ------------------------------------------------

                    calculate_maiden_overs(
                        deliveries,
                        stats,
                        player_ids
                    )

                    # ------------------------------------------------
                    # Process deliveries
                    # ------------------------------------------------

                    for delivery in deliveries:

                        batter_name = delivery.get(
                            "batter"
                        )

                        bowler_name = delivery.get(
                            "bowler"
                        )

                        # ----------------------------------------
                        # Batting
                        # ----------------------------------------

                        calculate_batting(
                            delivery,
                            stats,
                            player_ids
                        )

                        if batter_name:

                            batter_id = player_ids.get(
                                batter_name
                            )

                            if batter_id is None:
                                raise ValueError(
                                    f"No Cricsheet ID found "
                                    f"for batter "
                                    f"'{batter_name}' "
                                    f"in {filename}"
                                )

                            stats[batter_id][
                                "team"
                            ] = batting_team

                            innings_batters.add(
                                batter_id
                            )

                        # ----------------------------------------
                        # Bowling
                        # ----------------------------------------

                        calculate_bowling(
                            delivery,
                            stats,
                            player_ids
                        )

                        if bowler_name:

                            bowler_id = player_ids.get(
                                bowler_name
                            )

                            if bowler_id is None:
                                raise ValueError(
                                    f"No Cricsheet ID found "
                                    f"for bowler "
                                    f"'{bowler_name}' "
                                    f"in {filename}"
                                )

                            stats[bowler_id][
                                "team"
                            ] = fielding_team

                            innings_bowlers.add(
                                bowler_id
                            )

                        # ----------------------------------------
                        # Dismissals
                        # ----------------------------------------

                        calculate_dismissal(
                            delivery,
                            stats,
                            player_ids,
                            batting_team
                        )

                        # ----------------------------------------
                        # Fielding
                        # ----------------------------------------

                        calculate_fielding(
                            delivery,
                            stats,
                            player_ids,
                            fielding_team
                        )

                # ------------------------------------------------
                # Mark batting innings
                # ------------------------------------------------

                for player_id in innings_batters:

                    stats[player_id][
                        "batting_innings"
                    ] += 1

                # ------------------------------------------------
                # Mark bowling innings
                # ------------------------------------------------

                for player_id in innings_bowlers:

                    stats[player_id][
                        "bowling_innings"
                    ] += 1

            # ----------------------------------------------------
            # Build player-match records
            # ----------------------------------------------------

            for player_id, player in stats.items():

                # Resolve canonical name.
                #
                # This is the correct mapping variable:
                #
                # canonical_player_names
                #
                if player_id not in canonical_player_names:

                    raise ValueError(
                        f"Player ID "
                        f"{player_id} "
                        f"is missing from "
                        f"players.csv"
                    )

                player_name = (
                    canonical_player_names[
                        player_id
                    ]
                )

                # ------------------------------------------------
                # Only output players who actually participated
                # in the match.
                #
                # Fielding-only substitute players are included
                # because they have catches/stumpings/run-outs.
                # ------------------------------------------------

                participated = (
                        player["batting_innings"] > 0
                        or player["bowling_innings"] > 0
                        or player["catches"] > 0
                        or player["stumpings"] > 0
                        or player["run_outs"] > 0
                        or player["dismissals"] > 0
                )

                if not participated:
                    continue

                records.append({

                    "source_match_id":
                        match_id,

                    "season":
                        season,

                    "cricsheet_player_id":
                        player_id,

                    "player_name":
                        player_name,

                    "team":
                        player["team"],

                    # Batting
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

                    "dismissals":
                        player["dismissals"],

                    # Bowling
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

                    # Fielding
                    "catches":
                        player["catches"],

                    "stumpings":
                        player["stumpings"],

                    "run_outs":
                        player["run_outs"],
                })

                # ------------------------------------------------
                # Validation totals
                # ------------------------------------------------

                total_batting_runs += (
                    player["runs"]
                )

                total_balls_faced += (
                    player["balls_faced"]
                )

                total_fours += (
                    player["fours"]
                )

                total_sixes += (
                    player["sixes"]
                )

                total_dismissals += (
                    player["dismissals"]
                )

                total_bowling_runs += (
                    player["runs_conceded"]
                )

                total_legal_balls += (
                    player["balls_bowled"]
                )

                total_bowler_wickets += (
                    player["wickets"]
                )

                total_maidens += (
                    player["maidens"]
                )

                total_catches += (
                    player["catches"]
                )

                total_stumpings += (
                    player["stumpings"]
                )

                total_run_outs += (
                    player["run_outs"]
                )

            if index % 100 == 0:

                print(
                    f"Processed "
                    f"{index}/"
                    f"{len(json_files)} matches"
                )

    # ========================================================
    # WRITE CSV
    # ========================================================

    fieldnames = [
        "source_match_id",
        "season",

        "cricsheet_player_id",
        "player_name",
        "team",

        # Batting
        "batting_innings",
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "dismissals",

        # Bowling
        "bowling_innings",
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "maidens",

        # Fielding
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

        writer.writerows(
            records
        )

    # ========================================================
    # VALIDATION REPORT
    # ========================================================

    total_player_match_records = len(
        records
    )

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
            f"{total_matches}\n"
        )

        file.write(
            f"Player-match records: "
            f"{total_player_match_records}\n"
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
            f"Total batting dismissals: "
            f"{total_dismissals}\n"
        )

        file.write(
            f"Total bowling runs conceded: "
            f"{total_bowling_runs}\n"
        )

        file.write(
            f"Total legal balls bowled: "
            f"{total_legal_balls}\n"
        )

        file.write(
            f"Total bowling wickets credited: "
            f"{total_bowler_wickets}\n"
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

    # ========================================================
    # CONSOLE OUTPUT
    # ========================================================

    print("\n" + "=" * 70)
    print("PLAYER-MATCH STATISTICS GENERATED")
    print("=" * 70)

    print(
        f"Matches processed: "
        f"{total_matches}"
    )

    print(
        f"Player-match records: "
        f"{total_player_match_records}"
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
        f"Total batting dismissals: "
        f"{total_dismissals}"
    )

    print(
        f"Total fours: "
        f"{total_fours}"
    )

    print(
        f"Total sixes: "
        f"{total_sixes}"
    )

    print(
        f"Total bowling runs conceded: "
        f"{total_bowling_runs}"
    )

    print(
        f"Total legal balls bowled: "
        f"{total_legal_balls}"
    )

    print(
        f"Bowler wickets credited: "
        f"{total_bowler_wickets}"
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

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nValidation:")
    print(VALIDATION_FILE)


if __name__ == "__main__":
    build_player_match_stats()