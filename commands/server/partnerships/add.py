from pathlib import Path
from uuid import uuid4

from discord import Attachment, HTTPException, User

from bot import Cordex, Interaction, log
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import format_send
from core.state import (
    IMAGE_DIRECTORY,
    PartnershipEntry,
    load_partnership_data,
    save_partnership_data,
)
from guild_info.partnerships import rebuild_partnership_view

from ._base import INVITE_REGEX, get_channel

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server partnership add Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_server_partnership_add(
    bot                : Cordex,
    interaction        : Interaction,
    server_name        : str,
    server_picture     : Attachment,
    server_description : str,
    server_owner       : User,
    server_link        : str,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if not INVITE_REGEX.match(server_link):
        await send_bad_argument(interaction, subtitle = {"server-link" : "The server link must be a valid Discord invite."})
        return

    channel = await get_channel(interaction)
    if channel is None:
        return

    IMAGE_DIRECTORY.mkdir(parents = True, exist_ok = True)

    suffix     = Path(server_picture.filename).suffix or ".png"
    filename   = f"{uuid4()}{suffix}"
    image_path = IMAGE_DIRECTORY / filename

    try:
        image_bytes = await server_picture.read()
        image_path.write_bytes(image_bytes)

    except HTTPException:
        log.exception("Failed to download partnership attachment")
        await send_bad_operation(interaction, title = "download the server picture")
        raise

    except OSError:
        log.exception("Failed to save partnership attachment to disk")
        await send_bad_operation(interaction, title = "save the server picture")
        raise

    data        = await load_partnership_data(bot.db)
    description = server_description.replace("\\n", "\n")

    entry : PartnershipEntry = {
        "server_name"        : server_name,
        "server_description" : description,
        "server_owner_id"    : server_owner.id,
        "server_link"        : server_link,
        "image_filename"     : filename,
    }
    data["partnerships"].append(entry)

    await format_send(
        interaction,
        msg_type =  "success",
        title    = f"added partnership with {server_name}",
        subtitle =  "Updating the channel...",
    )

    try:
        await rebuild_partnership_view(bot, data["partnerships"])
        await save_partnership_data(bot.db, data)
    except HTTPException:
        log.exception("Failed to rebuild partnership layout after add")
        data["partnerships"].pop()
        image_path.unlink(missing_ok = True)
        await send_bad_operation(
            interaction,
            title    =  "update the partnerships channel",
            subtitle = f"**{server_name}** was added to the data but the channel failed to rebuild. The entry has been rolled back.",
        )
        raise
