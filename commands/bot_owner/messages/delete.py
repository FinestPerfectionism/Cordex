import discord
from discord.abc import Messageable

from bot import Interaction
from core.exceptions import send_bad_argument, send_unknown_error

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner delete Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_delete(
    interaction : Interaction,
    channel     : Messageable,
    message_id  : str,
) -> None:
    _ = await interaction.response.defer(ephemeral = True)

    try:
        try:
            target_message = await channel.fetch_message(int(message_id))
        except (discord.NotFound, ValueError, discord.HTTPException):
            await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist, I lack permissions to access it, or it is not a valid ID."})
            return

        if target_message.author != interaction.client.user:
            await send_bad_argument(interaction, subtitle = {"message-id" : "This messages was not sent by me, so I shouldn't delete it."})
            return

        await target_message.delete()
        await interaction.followup.send("Deleted!", ephemeral = True)

    except discord.Forbidden:
        _ = await send_unknown_error(interaction)
        return
