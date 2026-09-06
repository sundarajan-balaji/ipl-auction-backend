import csv
import os
import sys
from pathlib import Path

import psycopg2


# ============================================================
# PATHS
# ============================================================

DATA_DIR = Path(__file__).resolve().parents[2]

PLAYERS_FILE = (
        DATA_DIR
        / "processed"
        / "players.csv"
)


# ============================================================
# DATABASE
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


def get_connection():

    if DB_URL:
        return psycopg2.connect(DB_URL)

    if not DB_PASSWORD:

        print(
            "ERROR: DATABASE_PASSWORD is not set."
        )

        print(
            'PowerShell example:'
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
# IMPORT
# ============================================================

def build_players_db():

    print("=" * 70)
    print("PLAYER DATABASE IMPORT")
    print("=" * 70)

    if not PLAYERS_FILE.exists():

        raise FileNotFoundError(
            f"Players file not found:\n{PLAYERS_FILE}"
        )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Load CSV
        # ----------------------------------------------------

        with open(
                PLAYERS_FILE,
                "r",
                encoding="utf-8",
                newline="",
        ) as file:

            reader = csv.DictReader(file)

            rows = list(reader)

        print(
            f"\nPlayers in CSV: {len(rows)}"
        )

        # ----------------------------------------------------
        # Validate CSV
        # ----------------------------------------------------

        ids = set()

        for row in rows:

            cricsheet_id = (
                row["cricsheet_player_id"]
                .strip()
            )

            name = row["name"].strip()

            if not cricsheet_id:
                raise ValueError(
                    "Found player with empty CricSheet ID."
                )

            if not name:
                raise ValueError(
                    f"Found player with empty name: "
                    f"{cricsheet_id}"
                )

            if cricsheet_id in ids:

                raise ValueError(
                    f"Duplicate CricSheet player ID: "
                    f"{cricsheet_id}"
                )

            ids.add(cricsheet_id)

        # ----------------------------------------------------
        # Insert / update
        # ----------------------------------------------------

        inserted = 0
        updated = 0

        for row in rows:

            cricsheet_id = (
                row["cricsheet_player_id"]
                .strip()
            )

            name = row["name"].strip()

            cursor.execute(
                """
                SELECT id, name
                FROM players
                WHERE cricsheet_player_id = %s
                """,
                (cricsheet_id,),
            )

            existing = cursor.fetchone()

            if existing is None:

                cursor.execute(
                    """
                    INSERT INTO players (
                        cricsheet_player_id,
                        name
                    )
                    VALUES (%s, %s)
                    """,
                    (
                        cricsheet_id,
                        name,
                    ),
                )

                inserted += 1

            else:

                player_id, existing_name = existing

                if existing_name != name:

                    cursor.execute(
                        """
                        UPDATE players
                        SET
                            name = %s,
                            updated_at =
                                CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (
                            name,
                            player_id,
                        ),
                    )

                    updated += 1

        connection.commit()

        # ----------------------------------------------------
        # Verify
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM players
            """
        )

        total_players = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM players
            WHERE cricsheet_player_id IS NOT NULL
            """
        )

        total_with_ids = cursor.fetchone()[0]

        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)

        print(
            f"\nCSV players : {len(rows)}"
        )

        print(
            f"Inserted    : {inserted}"
        )

        print(
            f"Updated     : {updated}"
        )

        print(
            f"DB players  : {total_players}"
        )

        print(
            f"With IDs    : {total_with_ids}"
        )

        # ----------------------------------------------------
        # Final validation
        # ----------------------------------------------------

        if total_with_ids != len(rows):

            raise ValueError(
                "Database player count does not match "
                "players.csv."
            )

        print("\n" + "=" * 70)
        print("PLAYER DATABASE VALIDATION PASSED")
        print("=" * 70)

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    build_players_db()