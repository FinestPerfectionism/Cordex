from asyncio import AbstractEventLoop
from collections.abc import Iterable
from pathlib import Path
from sqlite3 import LEGACY_TRANSACTION_CONTROL
from sqlite3 import Connection as SqliteConnection
from string.templatelib import Template
from typing import Literal, cast, override

from aiosqlite import Connection as AiosqliteConnection
from aiosqlite import Cursor
from aiosqlite import connect as aiosqlite_connect
from aiosqlite.context import Result

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# State Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Connection(AiosqliteConnection):
    @override
    def execute(
        self,
        sql        : str              | Template,
        parameters : Iterable[object] | None = None,
    ) -> Result[Cursor]:
        if isinstance(sql, Template):
            if parameters is not None:
                error = "Cannot pass extra parameters when using a t-string."
                raise ValueError(error)

            return super().execute("?".join(sql.strings), tuple(sql.values))
        return super().execute(sql, parameters)


async def connect(
    database          : str               | Path,
    *,
    iter_chunk_size   : int                      = 64,
    loop              : AbstractEventLoop | None = None,
    timeout           : float                    = 5.0,  # ruff: ignore[async-function-with-timeout]
    detect_types      : int                      = 0,
    isolation_level   : Literal[
        "DEFERRED",
        "EXCLUSIVE",
        "IMMEDIATE",
    ]                                     | None = "DEFERRED",
    check_same_thread : bool                     = True,
    factory           : type[SqliteConnection]   = SqliteConnection,
    cached_statements : int                      = 128,
    uri               : bool                     = False,
    autocommit        : bool              | int  = LEGACY_TRANSACTION_CONTROL,
) -> Connection:
    raw_connection = await aiosqlite_connect(
        database          = database,
        iter_chunk_size   = iter_chunk_size,
        loop              = loop,
        timeout           = timeout,
        detect_types      = detect_types,
        isolation_level   = isolation_level,
        check_same_thread = check_same_thread,
        factory           = factory,
        cached_statements = cached_statements,
        uri               = uri,
        autocommit        = cast("bool", autocommit),
    )

    conn = cast("Connection", raw_connection)
    conn.__class__ = Connection
    return conn
