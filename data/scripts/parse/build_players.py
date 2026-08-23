from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict
import csv
import json


DATA_DIR = Path(__file__).resolve().parents[2]

ZIP_FILE = DATA_DIR / "raw" / "cricsheet" / "ipl_json.zip"
OUTPUT_DIR = DATA_DIR / "processed"

PLAYERS_FILE = OUTPUT_DIR / "players.csv"
TEAM_HISTORY_FILE = OUTPUT_DIR / "player_team_history.csv"


def build_players():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Canonical players
    #
    # player_id -> player_name
    # ---------------------------------------------------------

    players = {}

    # ---------------------------------------------------------
    # Player-team-season relationships
    #
    # (player_id, team, season)
    # ---------------------------------------------------------

    team_history = set()

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

            season = str(info.get("season"))

            # -------------------------------------------------
            # Cricsheet registry
            #
            # This contains players AND officials.
            # We use it only to resolve:
            #
            # name -> Cricsheet player ID
            # -------------------------------------------------

            registry = (
                info
                .get("registry", {})
                .get("people", {})
            )

            # -------------------------------------------------
            # 1. Players explicitly listed in info.players
            # -------------------------------------------------

            for team, team_players in (
                    info.get("players", {})
            ).items():

                for player_name in team_players:

                    player_id = registry.get(
                        player_name
                    )

                    if player_id is None:
                        raise ValueError(
                            f"No registry ID found for "
                            f"player '{player_name}' "
                            f"in {filename}"
                        )

                    players[player_id] = player_name

                    team_history.add(
                        (
                            player_id,
                            player_name,
                            team,
                            season
                        )
                    )

            # -------------------------------------------------
            # 2. Discover every person appearing in actual
            #    delivery data.
            #
            # This captures:
            #
            # - batters
            # - bowlers
            # - substitute fielders
            #
            # but DOES NOT automatically add registry-only
            # officials.
            # -------------------------------------------------

            for innings in match.get("innings", []):

                batting_team = innings.get("team")

                # Fielding team is the other team.
                fielding_team = next(
                    (
                        team
                        for team in info.get("teams", [])
                        if team != batting_team
                    ),
                    None
                )

                for over in innings.get(
                        "overs",
                        []
                ):

                    for delivery in over.get(
                            "deliveries",
                            []
                    ):

                        # -------------------------------------
                        # Batter
                        # -------------------------------------

                        batter_name = delivery.get(
                            "batter"
                        )

                        if batter_name:

                            player_id = registry.get(
                                batter_name
                            )

                            if player_id is None:
                                raise ValueError(
                                    f"No registry ID found "
                                    f"for batter "
                                    f"'{batter_name}' "
                                    f"in {filename}"
                                )

                            players[player_id] = (
                                batter_name
                            )

                            if batting_team:
                                team_history.add(
                                    (
                                        player_id,
                                        batter_name,
                                        batting_team,
                                        season
                                    )
                                )

                        # -------------------------------------
                        # Bowler
                        # -------------------------------------

                        bowler_name = delivery.get(
                            "bowler"
                        )

                        if bowler_name:

                            player_id = registry.get(
                                bowler_name
                            )

                            if player_id is None:
                                raise ValueError(
                                    f"No registry ID found "
                                    f"for bowler "
                                    f"'{bowler_name}' "
                                    f"in {filename}"
                                )

                            players[player_id] = (
                                bowler_name
                            )

                            if fielding_team:
                                team_history.add(
                                    (
                                        player_id,
                                        bowler_name,
                                        fielding_team,
                                        season
                                    )
                                )

                        # -------------------------------------
                        # Fielders
                        #
                        # This is important:
                        #
                        # A substitute fielder can appear
                        # here without appearing in
                        # info.players.
                        # -------------------------------------

                        for wicket in delivery.get(
                                "wickets",
                                []
                        ):

                            for fielder in wicket.get(
                                    "fielders",
                                    []
                            ):

                                fielder_name = fielder.get(
                                    "name"
                                )

                                if not fielder_name:
                                    continue

                                player_id = registry.get(
                                    fielder_name
                                )

                                if player_id is None:
                                    raise ValueError(
                                        f"No registry ID "
                                        f"found for fielder "
                                        f"'{fielder_name}' "
                                        f"in {filename}"
                                    )

                                players[player_id] = (
                                    fielder_name
                                )

                                if fielding_team:
                                    team_history.add(
                                        (
                                            player_id,
                                            fielder_name,
                                            fielding_team,
                                            season
                                        )
                                    )

            if index % 100 == 0:
                print(
                    f"Processed "
                    f"{index}/{len(json_files)} matches"
                )

    # ---------------------------------------------------------
    # Write players.csv
    # ---------------------------------------------------------

    with open(
            PLAYERS_FILE,
            "w",
            newline="",
            encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "cricsheet_player_id",
            "name"
        ])

        for player_id, player_name in sorted(
                players.items(),
                key=lambda item: item[1]
        ):

            writer.writerow([
                player_id,
                player_name
            ])

    # ---------------------------------------------------------
    # Write player_team_history.csv
    # ---------------------------------------------------------

    with open(
            TEAM_HISTORY_FILE,
            "w",
            newline="",
            encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "cricsheet_player_id",
            "player_name",
            "team",
            "season"
        ])

        for (
                player_id,
                player_name,
                team,
                season
        ) in sorted(
            team_history,
            key=lambda row: (
                    row[1],
                    row[3],
                    row[2]
            )
        ):

            writer.writerow([
                player_id,
                player_name,
                team,
                season
            ])

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("PLAYER DATASET GENERATED")
    print("=" * 60)

    print(
        f"Players: {len(players)}"
    )

    print(
        f"Player-team-season relationships: "
        f"{len(team_history)}"
    )

    print("\nPlayers file:")
    print(PLAYERS_FILE)

    print("\nTeam history file:")
    print(TEAM_HISTORY_FILE)


if __name__ == "__main__":
    build_players()