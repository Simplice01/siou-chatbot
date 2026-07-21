import os
import sys
from pathlib import Path

import psycopg


ROOT = Path(__file__).resolve().parents[2]
SQL_FILES = [
    ROOT / "database" / "schema.sql",
    ROOT / "database" / "seed_reference_data.sql",
]


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL est manquant.", file=sys.stderr)
        raise SystemExit(1)

    with psycopg.connect(database_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            for sql_file in SQL_FILES:
                print(f"Application de {sql_file.relative_to(ROOT)}")
                cursor.execute(sql_file.read_text(encoding="utf-8"))

    print("Base PostgreSQL SIOU initialisee.")


if __name__ == "__main__":
    main()

