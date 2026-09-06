import csv
import os
import sys
from pathlib import Path

import psycopg2


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path(__file__).resolve().parents[2]

MATCHES_FILE = DATA_DIR / "processed" / "matches.csv"


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_URL = os.getenv("DATABASE_URL")

DB_HOST = os.getenv(
    "DATABASE_HOST",
    "aws-0-ap-northeast-1.pooler.supabase.com",
)

DB_PORT = int(os.getenv("DATABASE_PORT", "5432"))

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
        print(
            '$env:DATABASE_PASSWORD="your-password"'
        )
        sys.exit(1)

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_city(city):

    if not city:
        return ""

    city = city.strip().lower()

    aliases = {
        "bangalore": "bengaluru",
        "chandigarh": "mohali",
    }

    return aliases.get(city, city)


# ============================================================
# LOAD TEAMS
# ============================================================

def load_teams(cursor):

    cursor.execute(
        """
        SELECT id, name
        FROM teams
        """
    )

    teams = {}

    for team_id, name in cursor.fetchall():
        teams[name] = team_id

    return teams


def load_team_aliases(cursor):

    cursor.execute(
        """
        SELECT alias_name, team_id
        FROM team_aliases
        """
    )

    aliases = {}

    for alias_name, team_id in cursor.fetchall():
        aliases[alias_name] = team_id

    return aliases


def resolve_team(
        name,
        teams,
        team_aliases,
):

    if not name:
        return None

    name = name.strip()

    if name in teams:
        return teams[name]

    if name in team_aliases:
        return team_aliases[name]

    return None


# ============================================================
# LOAD VENUES
# ============================================================

def load_venues(cursor):

    cursor.execute(
        """
        SELECT id, name, city
        FROM venues
        """
    )

    venues = {}

    for venue_id, name, city in cursor.fetchall():

        key = (
            name.strip().lower(),
            normalize_city(city),
        )

        venues.setdefault(key, []).append(
            venue_id
        )

    return venues


def load_venue_aliases(cursor):

    cursor.execute(
        """
        SELECT
            alias_name,
            alias_city,
            venue_id
        FROM venue_aliases
        """
    )

    aliases = {}

    for (
            alias_name,
            alias_city,
            venue_id,
    ) in cursor.fetchall():

        key = (
            alias_name.strip().lower(),
            normalize_city(alias_city),
        )

        aliases.setdefault(key, []).append(
            venue_id
        )

    return aliases


def resolve_venue(
        name,
        city,
        venues,
        venue_aliases,
):

    if not name:
        return None

    normalized_name = name.strip().lower()
    normalized_city = normalize_city(city)

    key = (
        normalized_name,
        normalized_city,
    )

    # Exact canonical match
    candidates = venues.get(key, [])

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        raise ValueError(
            f"Ambiguous canonical venue: "
            f"{name} | {city}"
        )

    # Exact alias match
    candidates = venue_aliases.get(key, [])

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        raise ValueError(
            f"Ambiguous venue alias: "
            f"{name} | {city}"
        )

    # Unique venue by name, ignoring city.
    all_candidates = []

    for (
            venue_key,
            venue_ids,
    ) in venues.items():

        if venue_key[0] == normalized_name:
            all_candidates.extend(venue_ids)

    all_candidates = list(set(all_candidates))

    if len(all_candidates) == 1:
        return all_candidates[0]

    # Unique alias by name, ignoring city.
    alias_candidates = []

    for (
            alias_key,
            venue_ids,
    ) in venue_aliases.items():

        if alias_key[0] == normalized_name:
            alias_candidates.extend(venue_ids)

    alias_candidates = list(
        set(alias_candidates)
    )

    if len(alias_candidates) == 1:
        return alias_candidates[0]

    return None


# ============================================================
# LOAD PLAYERS
# ============================================================

def load_players(cursor):

    cursor.execute(
        """
        SELECT id, cricsheet_player_id, name
        FROM players
        ORDER BY id
        """
    )

    players_by_name = {}

    for player_id, cricsheet_player_id, name in cursor.fetchall():

        players_by_name.setdefault(
            name,
            [],
        ).append(
            {
                "id": player_id,
                "cricsheet_player_id": cricsheet_player_id,
            }
        )

    return players_by_name

def load_player_team_history():

    history_file = (
            DATA_DIR
            / "processed"
            / "player_team_history.csv"
    )

    if not history_file.exists():
        raise FileNotFoundError(
            f"Player-team history file not found:\n"
            f"{history_file}"
        )

    history = {}

    with open(
            history_file,
            "r",
            encoding="utf-8",
            newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            player_id = row[
                "cricsheet_player_id"
            ].strip()

            player_name = row[
                "player_name"
            ].strip()

            team = row[
                "team"
            ].strip()

            season = row[
                "season"
            ].strip()

            key = (
                player_name,
                season,
                team,
            )

            history.setdefault(
                key,
                set(),
            ).add(player_id)

    return history

def resolve_player(
        name,
        season,
        team_1,
        team_2,
        players_by_name,
        player_team_history,
):

    if not name or not name.strip():
        return None

    name = name.strip()

    candidates = players_by_name.get(
        name,
        [],
    )

    if len(candidates) == 0:
        return None

    if len(candidates) == 1:
        return candidates[0]["id"]

    # --------------------------------------------------------
    # Duplicate player name.
    #
    # Resolve using the player's team history for this
    # particular season.
    # --------------------------------------------------------

    candidate_ids = set()

    for team in (team_1, team_2):

        key = (
            name,
            season,
            team,
        )

        historical_ids = (
            player_team_history.get(
                key,
                set(),
            )
        )

        candidate_ids.update(
            historical_ids
        )

    # Map CricSheet IDs back to database IDs.
    matching_db_ids = [
        candidate["id"]
        for candidate in candidates
        if candidate[
               "cricsheet_player_id"
           ] in candidate_ids
    ]

    matching_db_ids = list(
        set(matching_db_ids)
    )

    if len(matching_db_ids) == 1:
        return matching_db_ids[0]

    if len(matching_db_ids) == 0:
        raise ValueError(
            f"Could not disambiguate player "
            f"{name} for season {season}. "
            f"Teams: {team_1}, {team_2}. "
            f"Candidate IDs: "
            f"{[c['cricsheet_player_id'] for c in candidates]}"
        )

    raise ValueError(
        f"Ambiguous player "
        f"{name} for season {season}. "
        f"Teams: {team_1}, {team_2}. "
        f"Matching DB IDs: "
        f"{matching_db_ids}"
    )



# ============================================================
# VALIDATE CSV
# ============================================================

def load_match_rows():

    if not MATCHES_FILE.exists():

        raise FileNotFoundError(
            f"Matches file not found:\n"
            f"{MATCHES_FILE}"
        )

    with open(
            MATCHES_FILE,
            "r",
            encoding="utf-8",
            newline="",
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
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
# RESOLVE ALL MATCHES BEFORE INSERTING
# ============================================================

def normalize_result_type(value):

    if not value:
        return None

    value = value.strip().upper()

    aliases = {
        "WON_BY_RUNS": "WON_BY_RUNS",
        "WON_BY_WICKETS": "WON_BY_WICKETS",
        "TIE": "TIED",
        "TIED": "TIED",
        "NO_RESULT": "NO_RESULT",
        "RESULT_TIE": "TIED",
        "RESULT_NO_RESULT": "NO_RESULT",
    }

    normalized = aliases.get(value)

    if normalized is None:
        raise ValueError(
            f"Unknown result type: {value}"
        )

    return normalized

def resolve_matches(
        rows,
        teams,
        team_aliases,
        venues,
        venue_aliases,
        players_by_name,
        player_team_history,
):

    resolved = []

    for index, row in enumerate(rows, start=1):

        source_match_id = (
            row["source_match_id"].strip()
        )

        team_1_id = resolve_team(
            row["team_1"],
            teams,
            team_aliases,
        )

        team_2_id = resolve_team(
            row["team_2"],
            teams,
            team_aliases,
        )

        toss_winner_team_id = resolve_team(
            row["toss_winner"],
            teams,
            team_aliases,
        )

        winner_team_id = resolve_team(
            row["winner"],
            teams,
            team_aliases,
        )

        venue_id = resolve_venue(
            row["venue"],
            row["city"],
            venues,
            venue_aliases,
        )

        player_of_match_id = resolve_player(
            row["player_of_match"],
            row["season"].strip(),
            row["team_1"].strip(),
            row["team_2"].strip(),
            players_by_name,
            player_team_history,
        )

        errors = []

        if team_1_id is None:
            errors.append(
                f"team_1={row['team_1']}"
            )

        if team_2_id is None:
            errors.append(
                f"team_2={row['team_2']}"
            )

        if toss_winner_team_id is None:
            errors.append(
                f"toss_winner={row['toss_winner']}"
            )

        if row["winner"].strip() and winner_team_id is None:
            errors.append(
                f"winner={row['winner']}"
            )

        if venue_id is None:
            errors.append(
                f"venue={row['venue']} | "
                f"city={row['city']}"
            )

        if (
                row["player_of_match"].strip()
                and player_of_match_id is None
        ):
            errors.append(
                f"player_of_match="
                f"{row['player_of_match']}"
            )
        if errors:

            raise ValueError(
                f"Could not resolve match "
                f"{source_match_id}: "
                + "; ".join(errors)
            )

        season = row["season"].strip()

        if not season:
            raise ValueError(
                f"Missing season for match "
                f"{source_match_id}"
            )

        try:

            result_margin = (
                int(row["result_margin"])
                if row["result_margin"].strip()
                else None
            )

        except ValueError:

            raise ValueError(
                f"Invalid result margin for match "
                f"{source_match_id}: "
                f"{row['result_margin']}"
            )

        resolved.append(
            {
                "source_match_id": source_match_id,
                "season": season,
                "match_date": row["match_date"].strip(),
                "city": (
                    row["city"].strip()
                    if row["city"]
                    else None
                ),
                "venue_id": venue_id,
                "team_1_id": team_1_id,
                "team_2_id": team_2_id,
                "toss_winner_team_id":
                    toss_winner_team_id,
                "toss_decision":
                    row["toss_decision"].strip(),
                "winner_team_id":
                    winner_team_id,
                "result_type":
                    normalize_result_type(
                        row["result_type"]
                    ),
                "result_margin":
                    result_margin,
                "player_of_match_id":
                    player_of_match_id,
            }
        )

        if index % 100 == 0:
            print(
                f"Resolved {index}/{len(rows)} matches"
            )

    return resolved


# ============================================================
# INSERT
# ============================================================

def insert_matches(
        cursor,
        matches,
):

    inserted = 0
    skipped = 0

    for match in matches:

        cursor.execute(
            """
            INSERT INTO matches (
                source_match_id,
                season,
                match_date,
                city,
                venue_id,
                team_1_id,
                team_2_id,
                toss_winner_team_id,
                toss_decision,
                winner_team_id,
                result_type,
                result_margin,
                player_of_match_id
            )
            VALUES (
                       %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s,
                       %s, %s, %s
                   )
            ON CONFLICT (source_match_id)
                DO NOTHING
            """,
            (
                match["source_match_id"],
                match["season"],
                match["match_date"],
                match["city"],
                match["venue_id"],
                match["team_1_id"],
                match["team_2_id"],
                match["toss_winner_team_id"],
                match["toss_decision"],
                match["winner_team_id"],
                match["result_type"],
                match["result_margin"],
                match["player_of_match_id"],
            ),
        )

        if cursor.rowcount == 1:
            inserted += 1
        else:
            skipped += 1

    return inserted, skipped


# ============================================================
# VALIDATION
# ============================================================

def validate_database(
        cursor,
        expected_count,
):
    # --------------------------------------------------------
    # Basic record counts
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        """
    )

    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(DISTINCT source_match_id)
        FROM matches
        """
    )

    unique_source_ids = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Required fields
    #
    # These MUST exist for every match.
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE
            team_1_id IS NULL
           OR team_2_id IS NULL
           OR venue_id IS NULL
           OR toss_winner_team_id IS NULL
           OR toss_decision IS NULL
           OR toss_decision = ''
        """
    )

    incomplete = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Winning match consistency
    #
    # A match won by runs/wickets must have:
    #   - a winner
    #   - a result margin
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE
            result_type IN (
                            'WON_BY_RUNS',
                            'WON_BY_WICKETS'
                )
          AND (
            winner_team_id IS NULL
                OR result_margin IS NULL
            )
        """
    )

    invalid_wins = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Tie / no-result consistency
    #
    # Neither should have a winner.
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE
            result_type IN (
                            'TIED',
                            'NO_RESULT'
                )
          AND winner_team_id IS NOT NULL
        """
    )

    invalid_non_wins = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Winner must be one of the teams in the match
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE
            winner_team_id IS NOT NULL
          AND winner_team_id NOT IN (
                                     team_1_id,
                                     team_2_id
            )
        """
    )

    invalid_winner_team = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Toss winner must be one of the teams in the match
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE
            toss_winner_team_id IS NOT NULL
          AND toss_winner_team_id NOT IN (
                                          team_1_id,
                                          team_2_id
            )
        """
    )

    invalid_toss_winner = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Result margin must never be negative.
    #
    # The DB constraint already protects this, but keeping
    # the validation here makes the importer self-checking.
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM matches
        WHERE result_margin IS NOT NULL
          AND result_margin < 0
        """
    )

    invalid_margin = cursor.fetchone()[0]

    # --------------------------------------------------------
    # Print validation results
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("DATABASE VALIDATION")
    print("=" * 70)

    print(
        f"\nExpected matches       : {expected_count}"
    )

    print(
        f"Database matches       : {total}"
    )

    print(
        f"Unique source IDs      : {unique_source_ids}"
    )

    print(
        f"Invalid required rows  : {incomplete}"
    )

    print(
        f"Invalid winning results: {invalid_wins}"
    )

    print(
        f"Invalid tie/no-result  : {invalid_non_wins}"
    )

    print(
        f"Invalid winner teams   : {invalid_winner_team}"
    )

    print(
        f"Invalid toss winners   : {invalid_toss_winner}"
    )

    print(
        f"Invalid result margins : {invalid_margin}"
    )

    # --------------------------------------------------------
    # Assertions
    # --------------------------------------------------------

    if total != expected_count:
        raise ValueError(
            f"Expected {expected_count} matches "
            f"but database contains {total}."
        )

    if unique_source_ids != expected_count:
        raise ValueError(
            "source_match_id uniqueness validation failed."
        )

    if incomplete != 0:
        raise ValueError(
            "Found match records with missing "
            "required fields."
        )

    if invalid_wins != 0:
        raise ValueError(
            "Winning matches must have a winner "
            "and result margin."
        )

    if invalid_non_wins != 0:
        raise ValueError(
            "TIED/NO_RESULT matches must not have "
            "a winner."
        )

    if invalid_winner_team != 0:
        raise ValueError(
            "Winner must be one of the two teams "
            "participating in the match."
        )

    if invalid_toss_winner != 0:
        raise ValueError(
            "Toss winner must be one of the two teams "
            "participating in the match."
        )

    if invalid_margin != 0:
        raise ValueError(
            "Result margins cannot be negative."
        )

    print("\nAll match database checks passed.")


# ============================================================
# MAIN
# ============================================================

def build_matches_db():

    print("=" * 70)
    print("MATCH DATABASE IMPORT")
    print("=" * 70)

    rows = load_match_rows()

    print(
        f"\nMatches in CSV: {len(rows)}"
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        print("\nLoading database reference data...")

        teams = load_teams(cursor)
        team_aliases = load_team_aliases(cursor)

        venues = load_venues(cursor)
        venue_aliases = load_venue_aliases(cursor)

        players_by_name = load_players(cursor)

        player_team_history = load_player_team_history()

        print(
            f"Canonical teams : {len(teams)}"
        )

        print(
            f"Team aliases    : {len(team_aliases)}"
        )

        print(
            f"Canonical venues: "
            f"{len(set(
                venue_id
                for ids in venues.values()
                for venue_id in ids
            ))}"
        )

        print(
            f"Venue aliases   : {len(venue_aliases)}"
        )

        print(
            f"Player names    : {len(players_by_name)}"
        )

        print(
            f"Player IDs      : "
            f"{sum(
                len(ids)
                for ids in players_by_name.values()
            )}"
        )

        # ----------------------------------------------------
        # Resolve EVERYTHING before inserting anything.
        # ----------------------------------------------------

        print("\nResolving all matches...")

        resolved_matches = resolve_matches(
            rows,
            teams,
            team_aliases,
            venues,
            venue_aliases,
            players_by_name,
            player_team_history,
        )

        print(
            f"\nSuccessfully resolved "
            f"{len(resolved_matches)} matches."
        )

        # ----------------------------------------------------
        # Insert in one transaction.
        # ----------------------------------------------------

        print("\nInserting matches...")

        print("\nInserting matches...")

        inserted, skipped = insert_matches(
            cursor,
            resolved_matches,
        )

        print(
            f"Inserted : {inserted}"
        )

        print(
            f"Skipped  : {skipped}"
        )

        # ------------------------------------------------------------
        # Validate BEFORE committing.
        # ------------------------------------------------------------

        validate_database(
            cursor,
            len(rows),
        )

        # ------------------------------------------------------------
        # Only commit after every validation succeeds.
        # ------------------------------------------------------------

        connection.commit()

        print("\n" + "=" * 70)
        print("MATCH DATABASE IMPORT SUCCESSFUL")
        print("=" * 70)

        connection.commit()

        print(
            f"Inserted : {inserted}"
        )

        print(
            f"Skipped  : {skipped}"
        )

        # ----------------------------------------------------
        # Validate.
        # ----------------------------------------------------

        validate_database(
            cursor,
            len(rows),
        )

        print("\n" + "=" * 70)
        print("MATCH DATABASE IMPORT SUCCESSFUL")
        print("=" * 70)

    except Exception:

        connection.rollback()

        print(
            "\nTransaction rolled back. "
            "No partial match import was committed."
        )

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    build_matches_db()