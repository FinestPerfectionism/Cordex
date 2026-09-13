from collections.abc import Iterable
from pathlib import Path
from string.templatelib import Template
from typing import cast, override

from aiosqlite import Connection as AiosqliteConnection
from aiosqlite import Cursor
from aiosqlite import connect as aiosqlite_connect
from aiosqlite.context import Result

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# State Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class Connection(AiosqliteConnection):
    @override
    def execute(self, sql : str | Template, parameters : Iterable[object] | None = None) -> Result[Cursor]:
        if isinstance(sql, Template):
            if parameters is not None:
                error = "Cannot pass extra parameters when using a t-string."
                raise ValueError(error)

            return super().execute("?".join(sql.strings), tuple(sql.values))
        return super().execute(sql, parameters)


async def connect(database : str | Path) -> Connection:
    raw_connection = await aiosqlite_connect(database)

    conn = cast("Connection", raw_connection)
    conn.__class__ = Connection
    return conn
