from pathlib import Path
from typing import cast

from aiosqlite import Connection, Error
from typing_extensions import TypedDict

from bot import log

IMAGE_DIR : Path = Path("data/partnership_images")

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
        async with db.execute(
            "SELECT server_name, server_description, server_owner_id, server_link, image_filename FROM partnerships",
        ) as cursor:
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

        async with db.execute("SELECT timestamp FROM partnership_meta WHERE id = 0") as cursor:
            meta_row = await cursor.fetchone()

        timestamp : int = cast(int, meta_row[0]) if meta_row is not None else 0

        return {
            "partnerships" : partnerships,
            "timestamp"    : timestamp,
        }
    except Error:
        log.exception("Failed to load partnership data")
        return default()

async def save_partnership_data(db : Connection, data : PartnershipData) -> None:
    try:
        await db.execute("DELETE FROM partnerships")
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
            "UPDATE partnership_meta SET timestamp = ? WHERE id = 0",
            [str(data["timestamp"])],
        )

        await db.commit()
    except Error:
        log.exception("Failed to save partnership data")
