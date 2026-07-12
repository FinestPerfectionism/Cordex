from pathlib import Path
from uuid import uuid4

from discord import Attachment, HTTPException, User

from bot import Cordex, Interaction, log
from core.responses import format_send
from core.state import IMAGE_DIRECTORY, load_partnership_data, save_partnership_data
from guild_info.partnerships import rebuild_partnership_view

from ._base import INVITE_REGEX, get_channel

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server partnership update Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_server_partnership_update(
    bot                : Cordex,
    interaction        : Interaction,
    server_name        : str,
    server_picture     : Attachment | None = None,
    new_server_name    : str        | None = None,
    server_description : str        | None = None,
    server_owner       : User       | None = None,
    server_link        : str        | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if server_link is not None and not INVITE_REGEX.match(server_link):
        await format_send(
            interaction,
            msg_type = "warning",
            title    = "update partnership",
            subtitle = "The new server link must be a valid Discord invite.",
            footer   = "Bad argument",
        )
        return

    channel = await get_channel(interaction)
    if channel is None:
        return

    data    = await load_partnership_data(bot.db)
    matches = [p for p in data["partnerships"] if p["server_name"] == server_name]

    if not matches:
        await format_send(
            interaction,
            msg_type =  "warning",
            title    = f'find partnership "{server_name}"',
            subtitle =  "No partnership exists with that name. Check the spelling or use the autocomplete.",
            footer   =  "Bad argument",
        )
        return

    entry               = matches[0]
    old_image_filename  : str | None = None

    if server_picture is not None:
        IMAGE_DIRECTORY.mkdir(parents = True, exist_ok = True)
        suffix         = Path(server_picture.filename).suffix or ".png"
        new_filename   = f"{uuid4()}{suffix}"
        new_image_path = IMAGE_DIRECTORY / new_filename

        try:
            image_bytes = await server_picture.read()
            new_image_path.write_bytes(image_bytes)
            old_image_filename      = entry["image_filename"]
            entry["image_filename"] = new_filename

        except HTTPException:
            log.exception("Failed to download updated partnership attachment")
            await format_send(
                interaction,
                msg_type = "error",
                title    = "download the new server picture",
                subtitle = "Discord returned an error while fetching the attachment. No changes were saved.",
                footer   = "Bad operation",
            )
            return

        except OSError:
            log.exception("Failed to save updated partnership image to disk")
            await format_send(
                interaction,
                msg_type = "error",
                title    = "save the new server picture",
                subtitle = "The image was downloaded but could not be written to disk. No changes were saved.",
                footer   = "Bad operation",
            )
            return

    if new_server_name is not None:
        entry["server_name"] = new_server_name
    if server_description is not None:
        entry["server_description"] = server_description.replace("\\n", "\n")
    if server_owner is not None:
        entry["server_owner_id"] = server_owner.id
    if server_link is not None:
        entry["server_link"] = server_link

    display_name = entry["server_name"]

    await format_send(
        interaction,
        msg_type =  "success",
        title    = f"updated partnership with {server_name}",
        subtitle =  "Updating the channel...",
    )

    try:
        await rebuild_partnership_view(bot, data["partnerships"])

    except HTTPException:
        log.exception("Failed to rebuild partnership layout after update")
        await format_send(
            interaction,
            msg_type          =  "error",
            title             =  "update the partnerships channel",
            subtitle          = f"**{display_name}** was edited in the data but the channel failed to rebuild.",
            footer            =  "Bad operation",
        )
        return

    await save_partnership_data(bot.db, data)

    if old_image_filename is not None:
        (IMAGE_DIRECTORY / old_image_filename).unlink(missing_ok = True)
