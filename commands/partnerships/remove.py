from discord import HTTPException

from bot import Cordex, Interaction, log
from core.responses import format_send
from core.state import IMAGE_DIRECTORY, load_partnership_data, save_partnership_data
from guild_info.partnerships import rebuild_partnership_view

from ._base import get_channel

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /partnership remove Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_partnership_remove(
    bot         : Cordex,
    interaction : Interaction,
    server_name : str,
) -> None:
    await interaction.response.defer(ephemeral = True)

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

    removed  = matches[0]
    original = list(data["partnerships"])
    data["partnerships"] = [p for p in data["partnerships"] if p["server_name"] != server_name]

    await format_send(
        interaction,
        msg_type =  "success",
        title    = f"removed partnership with {server_name}",
        subtitle =  "Updating the channel...",
    )

    try:
        await rebuild_partnership_view(bot, data["partnerships"])

    except HTTPException:
        log.exception("Failed to rebuild partnership layout after remove")
        data["partnerships"] = original
        await save_partnership_data(bot.db, data)
        await format_send(
            interaction,
            msg_type =  "error",
            title    =  "update the partnerships channel",
            subtitle = f"**{server_name}** was removed from the data but the channel failed to rebuild. The entry has been restored.",
            footer   =  "Bad operation",
        )
        return

    await save_partnership_data(bot.db, data)

    (IMAGE_DIRECTORY / removed["image_filename"]).unlink(missing_ok = True)
