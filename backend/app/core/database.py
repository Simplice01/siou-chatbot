from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.core.config import Settings


class DatabaseUnavailableError(RuntimeError):
    pass


class Database:
    def __init__(self, settings: Settings) -> None:
        self.database_url = settings.database_url

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection[dict[str, Any]]]:
        if not self.database_url:
            raise DatabaseUnavailableError("DATABASE_URL n'est pas configure.")
        with psycopg.connect(self.database_url, row_factory=dict_row) as conn:
            yield conn
