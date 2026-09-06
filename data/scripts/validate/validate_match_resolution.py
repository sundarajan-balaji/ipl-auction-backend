import csv
import os
import sys
from pathlib import Path
from collections import Counter

import psycopg2


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path(__file__).resolve().parents[2]

MATCHES_FILE = (
        DATA_DIR
        / "processed"
        / "matches.csv"
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_URL = os.getenv("DATABASE_URL")

DB_HOST = os.getenv(
    "DATABASE_HOST",
    "aws-0-ap-northeast-1.pooler.supabase.com"
)

DB_PORT = int(
    os.getenv("DATABASE_PORT", "5432")
)

DB_NAME = os.getenv(
    "DATABASE_NAME",
    "postgres"
)

DB_USER = os.getenv(
    "DATABASE_USERNAME",
    "postgres.jpdryxehntfxarbnofzv"
)

DB_PASSWORD = os.getenv("DATABASE_PASSWORD")


def get_connection():
    """
    Prefer DATABASE_URL when available.

    Otherwise use individual database environment variables.

    Do not hard-code credentials into this script.
    """

    if DB_URL:
        return psycopg2.connect(DB_URL)

    if not DB_PASSWORD:
        print(
            "ERROR: DATABASE_PASSWORD environment variable "
            "is not set."
        )

        print()
        print(
            "Set it in PowerShell before running this script:"
        )

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
# LOAD DATABASE LOOKUPS
# ============================================================

def load_teams(cursor):

    cursor.execute(
        """
        SELECT id, name, short_code
        FROM teams
        """
    )

    teams_by_name = {}
    teams_by_code = {}

    for row in cursor.fetchall():

        team_id, name, short_code = row

        teams_by_name[name] = {
            "id": team_id,
            "name": name,
            "short_code": short_code,
        }

        teams_by_code[short_code] = {
            "id": team_id,
            "name": name,
            "short_code": short_code,
        }

    return teams_by_name, teams_by_code


def load_team_aliases(cursor):

    cursor.execute(
        """
        SELECT
            ta.alias_name,
            ta.team_id,
            t.name,
            t.short_code
        FROM team_aliases ta
                 JOIN teams t
                      ON t.id = ta.team_id
        """
    )

    aliases = {}

    for row in cursor.fetchall():

        alias_name, team_id, team_name, short_code = row

        aliases[alias_name] = {
            "id": team_id,
            "name": team_name,
            "short_code": short_code,
        }

    return aliases


def load_venues(cursor):

    cursor.execute(
        """
        SELECT id, name, city, country
        FROM venues
        """
    )

    venues = {}

    for row in cursor.fetchall():

        venue_id, name, city, country = row

        key = (
            name.strip().lower(),
            normalize_city(city),
        )

        venues[key] = {
            "id": venue_id,
            "name": name,
            "city": city,
            "country": country,
        }

    return venues


def load_venue_aliases(cursor):

    cursor.execute(
        """
        SELECT
            va.alias_name,
            va.alias_city,
            va.venue_id,
            v.name,
            v.city,
            v.country
        FROM venue_aliases va
                 JOIN venues v
                      ON v.id = va.venue_id
        """
    )

    aliases = {}

    for row in cursor.fetchall():

        (
            alias_name,
            alias_city,
            venue_id,
            venue_name,
            venue_city,
            country,
        ) = row

        key = (
            alias_name.strip().lower(),
            normalize_city(alias_city),
        )

        aliases[key] = {
            "id": venue_id,
            "name": venue_name,
            "city": venue_city,
            "country": country,
        }

    return aliases


def load_players(cursor):

    cursor.execute(
        """
        SELECT id, cricsheet_player_id, name
        FROM players
        """
    )

    players_by_name = {}

    for row in cursor.fetchall():

        player_id, cricsheet_id, name = row

        players_by_name[name] = {
            "id": player_id,
            "cricsheet_player_id": cricsheet_id,
            "name": name,
        }

    return players_by_name


# ============================================================
# RESOLUTION
# ============================================================

def resolve_team(
        raw_name,
        teams_by_name,
        team_aliases,
):

    if not raw_name:
        return None

    raw_name = raw_name.strip()

    # Canonical name
    if raw_name in teams_by_name:
        return teams_by_name[raw_name]

    # Historical alias
    if raw_name in team_aliases:
        return team_aliases[raw_name]

    return None


def normalize_city(city):
    """
    Normalize known city-name variations found in the
    CricSheet IPL dataset.
    """

    if not city:
        return ""

    city = city.strip().lower()

    city_aliases = {
        "bangalore": "bengaluru",
        "chandigarh": "mohali",
    }

    return city_aliases.get(city, city)


def resolve_venue(
        raw_name,
        city,
        venues,
        venue_aliases,
):

    if not raw_name:
        return None

    raw_name = raw_name.strip()
    normalized_name = raw_name.lower()

    normalized_city = normalize_city(city)

    # ------------------------------------------------------------
    # 1. Exact canonical venue + normalized city
    # ------------------------------------------------------------

    key = (
        normalized_name,
        normalized_city,
    )

    if key in venues:
        return venues[key]

    # ------------------------------------------------------------
    # 2. Exact alias + normalized city
    # ------------------------------------------------------------

    if key in venue_aliases:
        return venue_aliases[key]

    # ------------------------------------------------------------
    # 3. Unique canonical venue by name
    #
    #    This handles cases where CricSheet and our canonical
    #    data use different city names for the same venue.
    # ------------------------------------------------------------

    canonical_candidates = [
        venue
        for venue_key, venue in venues.items()
        if venue_key[0] == normalized_name
    ]

    if len(canonical_candidates) == 1:
        return canonical_candidates[0]

    # ------------------------------------------------------------
    # 4. Unique alias by name
    # ------------------------------------------------------------

    alias_candidates = [
        venue
        for alias_key, venue in venue_aliases.items()
        if alias_key[0] == normalized_name
    ]

    if len(alias_candidates) == 1:
        return alias_candidates[0]

    # ------------------------------------------------------------
    # 5. No safe resolution
    # ------------------------------------------------------------

    return None


def resolve_player(
        raw_name,
        players_by_name,
):

    if not raw_name:
        return None

    raw_name = raw_name.strip()

    return players_by_name.get(raw_name)


# ============================================================
# VALIDATION
# ============================================================

def validate_match_resolution():

    print("=" * 70)
    print("MATCH RESOLUTION VALIDATION")
    print("=" * 70)

    if not MATCHES_FILE.exists():

        raise FileNotFoundError(
            f"Matches file not found:\n{MATCHES_FILE}"
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        print("\nLoading database reference data...")

        teams_by_name, teams_by_code = load_teams(
            cursor
        )

        team_aliases = load_team_aliases(
            cursor
        )

        venues = load_venues(
            cursor
        )

        venue_aliases = load_venue_aliases(
            cursor
        )

        players_by_name = load_players(
            cursor
        )

        print(
            f"Canonical teams : {len(teams_by_name)}"
        )

        print(
            f"Team aliases    : {len(team_aliases)}"
        )

        print(
            f"Canonical venues: {len(venues)}"
        )

        print(
            f"Venue aliases   : {len(venue_aliases)}"
        )

        print(
            f"Players         : {len(players_by_name)}"
        )

        print("\nProcessing matches...")

        total = 0

        unresolved_teams = []
        unresolved_venues = []
        unresolved_players = []

        resolved_team_aliases = Counter()
        resolved_venue_aliases = Counter()

        with open(
                MATCHES_FILE,
                "r",
                encoding="utf-8",
                newline="",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                total += 1

                match_id = row["source_match_id"]

                # ------------------------------------------------
                # Teams
                # ------------------------------------------------

                team_1 = resolve_team(
                    row["team_1"],
                    teams_by_name,
                    team_aliases,
                )

                team_2 = resolve_team(
                    row["team_2"],
                    teams_by_name,
                    team_aliases,
                )

                toss_winner = resolve_team(
                    row["toss_winner"],
                    teams_by_name,
                    team_aliases,
                )

                winner = resolve_team(
                    row["winner"],
                    teams_by_name,
                    team_aliases,
                )

                team_values = {
                    "team_1": team_1,
                    "team_2": team_2,
                    "toss_winner": toss_winner,
                    "winner": winner,
                }

                for field, resolved in team_values.items():

                    raw_value = row[field]

                    if raw_value and not resolved:

                        unresolved_teams.append(
                            (
                                match_id,
                                field,
                                raw_value,
                            )
                        )

                    elif (
                            raw_value
                            and raw_value in team_aliases
                    ):

                        resolved_team_aliases[
                            raw_value
                        ] += 1

                # ------------------------------------------------
                # Venue
                # ------------------------------------------------

                venue = resolve_venue(
                    row["venue"],
                    row["city"],
                    venues,
                    venue_aliases,
                )

                if not venue:

                    unresolved_venues.append(
                        (
                            match_id,
                            row["venue"],
                            row["city"],
                        )
                    )

                else:

                    key = (
                        row["venue"].strip().lower(),
                        row["city"].strip().lower(),
                    )

                    if key in venue_aliases:

                        resolved_venue_aliases[
                            row["venue"]
                        ] += 1

                # ------------------------------------------------
                # Player of Match
                # ------------------------------------------------

                player_of_match = resolve_player(
                    row["player_of_match"],
                    players_by_name,
                )

                if (
                        row["player_of_match"]
                        and not player_of_match
                ):

                    unresolved_players.append(
                        (
                            match_id,
                            row["player_of_match"],
                        )
                    )

                if total % 100 == 0:

                    print(
                        f"Processed {total} matches"
                    )

        # ========================================================
        # RESULTS
        # ========================================================

        print("\n" + "=" * 70)
        print("RESULT")
        print("=" * 70)

        print(
            f"\nMatches processed: {total}"
        )

        print(
            f"Unresolved team references : "
            f"{len(unresolved_teams)}"
        )

        print(
            f"Unresolved venue references: "
            f"{len(unresolved_venues)}"
        )

        print(
            f"Unresolved player references: "
            f"{len(unresolved_players)}"
        )

        # --------------------------------------------------------
        # TEAM ALIASES
        # --------------------------------------------------------

        print("\n" + "-" * 70)
        print("TEAM ALIASES USED")
        print("-" * 70)

        if resolved_team_aliases:

            for name, count in sorted(
                    resolved_team_aliases.items()
            ):

                print(
                    f"{name}: {count}"
                )

        else:

            print("None")

        # --------------------------------------------------------
        # VENUE ALIASES
        # --------------------------------------------------------

        print("\n" + "-" * 70)
        print("VENUE ALIASES USED")
        print("-" * 70)

        if resolved_venue_aliases:

            for name, count in sorted(
                    resolved_venue_aliases.items()
            ):

                print(
                    f"{name}: {count}"
                )

        else:

            print("None")

        # --------------------------------------------------------
        # UNRESOLVED DETAILS
        # --------------------------------------------------------

        if unresolved_teams:

            print("\n" + "-" * 70)
            print("UNRESOLVED TEAMS")
            print("-" * 70)

            for (
                    match_id,
                    field,
                    value,
            ) in unresolved_teams[:50]:

                print(
                    f"{match_id} | "
                    f"{field} | "
                    f"{value}"
                )

        if unresolved_venues:

            print("\n" + "-" * 70)
            print("UNRESOLVED VENUES")
            print("-" * 70)

            for (
                    match_id,
                    venue,
                    city,
            ) in unresolved_venues[:50]:

                print(
                    f"{match_id} | "
                    f"{venue} | "
                    f"{city}"
                )

        if unresolved_players:

            print("\n" + "-" * 70)
            print("UNRESOLVED PLAYERS OF MATCH")
            print("-" * 70)

            for (
                    match_id,
                    player,
            ) in unresolved_players[:50]:

                print(
                    f"{match_id} | "
                    f"{player}"
                )

        # ========================================================
        # FINAL STATUS
        # ========================================================

        if (
                unresolved_teams
                or unresolved_venues
                or unresolved_players
        ):

            print("\n" + "=" * 70)
            print(
                "MATCH RESOLUTION VALIDATION FAILED"
            )
            print("=" * 70)

            raise ValueError(
                "One or more match references "
                "could not be resolved."
            )

        print("\n" + "=" * 70)
        print(
            "ALL MATCH REFERENCES RESOLVED SUCCESSFULLY"
        )
        print("=" * 70)

    finally:

        connection.close()


if __name__ == "__main__":
    validate_match_resolution()