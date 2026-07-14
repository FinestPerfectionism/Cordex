from typing import TypedDict, cast

from aiosqlite import Connection

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Ticket State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TicketRecord(TypedDict):
    thread_id : int
    team      : str
    open      : bool


async def save_ticket(db : Connection, *, thread_id : int, team : str) -> None:
    await db.execute(
        "INSERT INTO tickets (thread_id, team, open) VALUES (?, ?, 1)",
        (thread_id, team),
    )
    await db.commit()


async def set_ticket_state(db : Connection, *, thread_id : int, is_open : bool) -> None:
    await db.execute(
        "UPDATE tickets SET open = ? WHERE thread_id = ?",
        (int(is_open), thread_id),
    )
    await db.commit()


async def set_ticket_team(db : Connection, *, thread_id : int, team : str) -> None:
    await db.execute(
        "UPDATE tickets SET team = ? WHERE thread_id = ?",
        (team, thread_id),
    )
    await db.commit()


async def get_ticket(db : Connection, *, thread_id : int) -> TicketRecord | None:
    async with db.execute(
        "SELECT thread_id, team, open FROM tickets WHERE thread_id = ?",
        (thread_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if row is None:
        return None

    return TicketRecord(
        thread_id = cast(int, row[0]),
        team      = cast(str, row[1]),
        open      = bool(cast(int, row[2])),
    )


async def delete_ticket(db : Connection, *, thread_id : int) -> None:
    await db.execute(
        "DELETE FROM tickets WHERE thread_id = ?",
        (thread_id,),
    )
    await db.commit()
