from logging import getLogger as get_logger
from pathlib import Path
from typing import TypedDict, cast

from aiosqlite import Connection, Error

log = get_logger("Cordex")

IMAGE_DIRECTORY : Path = Path("data/partnership_images")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Partnership State Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class PartnershipEntry(TypedDict):
    server_name        : str
    server_description : str
    server_owner_id    : int
    server_link        : str
    image_filename     : str

class PartnershipData(TypedDict):
    partnerships : list[PartnershipEntry]
    timestamp    : int

def default() -> PartnershipData:
    return {
        "partnerships" : [],
        "timestamp"    : 0,
    }

async def load_partnership_data(db : Connection) -> PartnershipData:
    try:
        async with db.execute("SELECT server_name, server_description, server_owner_id, server_link, image_filename FROM partnerships WHERE id != 0") as cursor:
            partnership_rows = await cursor.fetchall()

        partnerships : list[PartnershipEntry] = [
            {
                "server_name"        : cast(str, row[0]),
                "server_description" : cast(str, row[1]),
                "server_owner_id"    : cast(int, row[2]),
                "server_link"        : cast(str, row[3]),
                "image_filename"     : cast(str, row[4]),
            }
            for row in partnership_rows
        ]

        async with db.execute("SELECT timestamp FROM partnerships WHERE id = 0") as cursor:
            meta_row = await cursor.fetchone()

        timestamp : int = cast(int, meta_row[0]) if meta_row is not None else 0

    except Error:
        log.exception("Failed to load partnership data")
        return default()
    else:
        return {
            "partnerships" : partnerships,
            "timestamp"    : timestamp,
        }


async def save_partnership_data(db : Connection, data : PartnershipData) -> None:
    try:
        await db.execute("DELETE FROM partnerships WHERE id != 0")
        await db.executemany(
            "INSERT INTO partnerships (server_name, server_description, server_owner_id, server_link, image_filename) VALUES (?, ?, ?, ?, ?)",
            [
                (
                    entry["server_name"],
                    entry["server_description"],
                    entry["server_owner_id"],
                    entry["server_link"],
                    entry["image_filename"],
                )
                for entry in data["partnerships"]
            ],
        )

        await db.execute(
            "UPDATE partnerships SET timestamp = ? WHERE id = 0",
            [str(data["timestamp"])],
        )

        await db.commit()
    except Error:
        log.exception("Failed to save partnership data")
