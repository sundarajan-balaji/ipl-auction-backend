import csv
import os
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path(__file__).resolve().parents[2]

STATS_FILE = (
        DATA_DIR
        / "processed"
        / "player_match_stats.csv"
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_URL = os.getenv("DATABASE_URL")

DB_HOST = os.getenv(
    "DATABASE_HOST",
    "aws-0-ap-northeast-1.pooler.supabase.com",
)

DB_PORT = int(
    os.getenv("DATABASE_PORT", "5432")
)

DB_NAME = os.getenv(
    "DATABASE_NAME",
    "postgres",
)

DB_USER = os.getenv(
    "DATABASE_USERNAME",
    "postgres.jpdryxehntfxarbnofzv",
)

DB_PASSWORD = os.getenv("DATABASE_PASSWORD")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    if DB_URL:
        return psycopg2.connect(DB_URL)

    if not DB_PASSWORD:
        print("ERROR: DATABASE_PASSWORD is not set.")
        print()
        print('$env:DATABASE_PASSWORD="your-password"')
        sys.exit(1)

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# ============================================================
# LOAD CSV
# ============================================================

def load_stats_rows():

    if not STATS_FILE.exists():
        raise FileNotFoundError(
            f"Statistics file not found:\n{STATS_FILE}"
        )

    with open(
            STATS_FILE,
            "r",
            encoding="utf-8",
            newline="",
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
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
            "dismissals",
            "bowling_innings",
            "runs_conceded",
            "balls_bowled",
            "wickets",
            "maidens",
            "catches",
            "stumpings",
            "run_outs",
        }

        actual_columns = set(
            reader.fieldnames or []
        )

        missing = (
                required_columns
                - actual_columns
        )

        if missing:
            raise ValueError(
                f"Missing CSV columns: "
                f"{sorted(missing)}"
            )

        rows = list(reader)

    return rows


# ============================================================
# MAIN
# ============================================================

def load_players(cursor):

    cursor.execute("""
                   SELECT id, cricsheet_player_id
                   FROM players
                   """)

    return {
        cricsheet_player_id: player_id
        for player_id, cricsheet_player_id in cursor.fetchall()
    }

def load_matches(cursor):

    cursor.execute("""
                   SELECT
                       m.id,
                       m.source_match_id,
                       m.season,
                       m.team_1_id,
                       m.team_2_id
                   FROM matches m
                   """)

    return {
        source_match_id: {
            "id": match_id,
            "season": season,
            "team_1_id": team_1_id,
            "team_2_id": team_2_id,
        }
        for (
            match_id,
            source_match_id,
            season,
            team_1_id,
            team_2_id,
        ) in cursor.fetchall()
    }

def load_teams(cursor):

    cursor.execute("""
                   SELECT id, name
                   FROM teams
                   """)

    return {
        team_id: name
        for team_id, name in cursor.fetchall()
    }

def get_season_year(season):
    """
    Return the possible calendar years represented by a
    Cricsheet season value.

    Examples:
        2007/08 -> (2007, 2008)
        2009/10 -> (2009, 2010)
        2020/21 -> (2020, 2021)
        2024   -> (2024,)
    """

    if "/" in season:
        start_year, end_year = season.split("/", 1)

        start_year = int(start_year)

        if len(end_year) == 2:
            end_year = int(
                start_year // 100 * 100 + int(end_year)
            )
        else:
            end_year = int(end_year)

        return start_year, end_year

    return (int(season),)

def resolve_team_id(team_name, season, match, teams, team_aliases):

    season_years = get_season_year(season)

    participating_team_ids = {
        match["team_1_id"],
        match["team_2_id"],
    }

    # First check canonical team names.
    for team_id in participating_team_ids:

        if teams[team_id].strip().lower() == team_name.strip().lower():
            return team_id

    # Then check historical aliases.
    for (
            team_id,
            alias_name,
            valid_from_season,
            valid_to_season,
    ) in team_aliases:

        if team_id not in participating_team_ids:
            continue

        if alias_name.strip().lower() != team_name.strip().lower():
            continue

        if any(
                valid_from_season <= season_year <= valid_to_season
                for season_year in season_years
        ):
            return team_id

    return None

def validate_rows(
        rows,
        players,
        matches,
        teams,
        team_aliases
):
    unresolved_players = []
    unresolved_matches = []
    unresolved_teams = []
    duplicate_records = []

    resolved_records = []

    seen_records = set()

    for row_number, row in enumerate(rows, start=2):

        source_match_id = int(row["source_match_id"])

        player_id = players.get(
            row["cricsheet_player_id"]
        )

        match = matches.get(source_match_id)

        # --------------------------------------------------------
        # Player reference
        # --------------------------------------------------------

        if player_id is None:
            unresolved_players.append(
                (
                    row_number,
                    row["cricsheet_player_id"]
                )
            )
            continue

        # --------------------------------------------------------
        # Match reference
        # --------------------------------------------------------

        if match is None:
            unresolved_matches.append(
                (
                    row_number,
                    source_match_id
                )
            )
            continue

        # --------------------------------------------------------
        # Team reference
        # --------------------------------------------------------

        team_id = resolve_team_id(
            row["team"],
            match["season"],
            match,
            teams,
            team_aliases
        )

        if team_id is None:
            unresolved_teams.append(
                (
                    row_number,
                    source_match_id,
                    match["season"],
                    row["team"]
                )
            )
            continue

        # --------------------------------------------------------
        # Database uniqueness constraint
        # (match_id, player_id)
        # --------------------------------------------------------

        record_key = (
            match["id"],
            player_id
        )

        if record_key in seen_records:
            duplicate_records.append(
                (
                    row_number,
                    source_match_id,
                    row["cricsheet_player_id"]
                )
            )
            continue

        seen_records.add(record_key)

        # --------------------------------------------------------
        # Build resolved record
        # --------------------------------------------------------

        resolved_records.append({
            "match_id": match["id"],
            "player_id": player_id,
            "team_id": team_id,

            "batting_innings": int(
                row["batting_innings"]
            ),
            "runs": int(
                row["runs"]
            ),
            "balls_faced": int(
                row["balls_faced"]
            ),
            "fours": int(
                row["fours"]
            ),
            "sixes": int(
                row["sixes"]
            ),
            "dismissals": int(
                row["dismissals"]
            ),

            "bowling_innings": int(
                row["bowling_innings"]
            ),
            "runs_conceded": int(
                row["runs_conceded"]
            ),
            "balls_bowled": int(
                row["balls_bowled"]
            ),
            "wickets": int(
                row["wickets"]
            ),
            "maidens": int(
                row["maidens"]
            ),

            "catches": int(
                row["catches"]
            ),
            "stumpings": int(
                row["stumpings"]
            ),
            "run_outs": int(
                row["run_outs"]
            ),
        })

    return (
        resolved_records,
        unresolved_players,
        unresolved_matches,
        unresolved_teams,
        duplicate_records
    )

def import_stats(cursor, records):
    """
    Insert validated player-match statistics into the database.

    Existing (match_id, player_id) records are updated so that
    the importer is idempotent.
    """

    sql = """
          INSERT INTO player_match_stats (
              match_id,
              player_id,
              team_id,
              batting_innings,
              runs,
              balls_faced,
              fours,
              sixes,
              dismissals,
              bowling_innings,
              runs_conceded,
              balls_bowled,
              wickets,
              maidens,
              catches,
              stumpings,
              run_outs
          )
          VALUES %s
        ON CONFLICT (match_id, player_id)
          DO UPDATE SET
          team_id = EXCLUDED.team_id,
          batting_innings = EXCLUDED.batting_innings,
          runs = EXCLUDED.runs,
          balls_faced = EXCLUDED.balls_faced,
          fours = EXCLUDED.fours,
          sixes = EXCLUDED.sixes,
          dismissals = EXCLUDED.dismissals,
          bowling_innings = EXCLUDED.bowling_innings,
          runs_conceded = EXCLUDED.runs_conceded,
          balls_bowled = EXCLUDED.balls_bowled,
          wickets = EXCLUDED.wickets,
          maidens = EXCLUDED.maidens,
          catches = EXCLUDED.catches,
          stumpings = EXCLUDED.stumpings,
          run_outs = EXCLUDED.run_outs,
          updated_at = CURRENT_TIMESTAMP \
          """

    values = [
        (
            record["match_id"],
            record["player_id"],
            record["team_id"],
            record["batting_innings"],
            record["runs"],
            record["balls_faced"],
            record["fours"],
            record["sixes"],
            record["dismissals"],
            record["bowling_innings"],
            record["runs_conceded"],
            record["balls_bowled"],
            record["wickets"],
            record["maidens"],
            record["catches"],
            record["stumpings"],
            record["run_outs"],
        )
        for record in records
    ]

    execute_values(
        cursor,
        sql,
        values,
        page_size=1000
    )

    print(
        f"Imported {len(records)} player-match records."
    )

def load_team_aliases(cursor):

    cursor.execute("""
                   SELECT
                       team_id,
                       alias_name,
                       valid_from_season,
                       valid_to_season
                   FROM team_aliases
                   """)

    return [
        (
            team_id,
            alias_name,
            int(valid_from_season),
            int(valid_to_season),
        )
        for (
            team_id,
            alias_name,
            valid_from_season,
            valid_to_season,
        ) in cursor.fetchall()
    ]

def main():

    print("=" * 70)
    print("PLAYER-MATCH STATISTICS DATABASE IMPORT")
    print("=" * 70)

    rows = load_stats_rows()

    print(
        f"\nStatistics records in CSV: {len(rows)}"
    )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            players = load_players(cursor)
            matches = load_matches(cursor)
            teams = load_teams(cursor)
            team_aliases = load_team_aliases(cursor)

            (
                resolved_records,
                unresolved_players,
                unresolved_matches,
                unresolved_teams,
                duplicate_records
            ) = validate_rows(
                rows,
                players,
                matches,
                teams,
                team_aliases
            )

            print(
                f"Players loaded: {len(players)}"
            )

            print(
                f"Matches loaded: {len(matches)}"
            )

            print(
                f"Teams loaded: {len(teams)}"
            )

            print(
                f"Team aliases loaded: {len(team_aliases)}"
            )

            print()
            print("VALIDATION RESULTS")
            print("-" * 70)

            print(
                f"Unresolved player references : "
                f"{len(unresolved_players)}"
            )

            print(
                f"Unresolved match references  : "
                f"{len(unresolved_matches)}"
            )

            print(
                f"Unresolved team references   : "
                f"{len(unresolved_teams)}"
            )

            print(
                f"Duplicate records            : "
                f"{len(duplicate_records)}"
            )

            if unresolved_teams:

                print()
                print("UNRESOLVED TEAM EXAMPLES")
                print("-" * 70)

                unique_unresolved_teams = sorted(
                    set(
                        (
                            source_match_id,
                            season,
                            team_name
                        )
                        for (
                            row_number,
                            source_match_id,
                            season,
                            team_name
                        ) in unresolved_teams
                    )
                )

                for (
                        source_match_id,
                        season,
                        team_name
                ) in unique_unresolved_teams[:50]:

                    print(
                        f"Match {source_match_id} | "
                        f"Season {season} | "
                        f"Team: {team_name}"
                    )

                print()
                print(
                    f"Showing first "
                    f"{min(50, len(unique_unresolved_teams))} "
                    f"unique unresolved combinations."
                )

            if (
                    not unresolved_players
                    and not unresolved_matches
                    and not unresolved_teams
                    and not duplicate_records
            ):
                print()
                print("Validation passed.")
                print("Importing statistics...")

                import_stats(
                    cursor,
                    resolved_records
                )

                connection.commit()

                print("Database import committed successfully.")
            else:
                print()
                print("Validation failed.")
                print("No database changes were made.")

                connection.rollback()

    finally:
        connection.close()


if __name__ == "__main__":
    main()