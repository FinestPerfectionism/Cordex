import discord
from discord.abc import Messageable

from bot import Interaction
from commands.bot_owner._base import emoji_inaccessible
from core.exceptions import send_bad_argument, send_unknown_error

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner edit Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_edit(
    interaction : Interaction,
    channel     : Messageable,
    text        : str,
    message_id  : str,
) -> None:
    _ = await interaction.response.defer(ephemeral = True)

    async def do_edit(interaction : Interaction) -> None:
        try:
            try:
                target_message = await channel.fetch_message(int(message_id))

            except (discord.NotFound, ValueError, discord.HTTPException):
                await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist, I lack permissions to access it, or it is not a valid ID."})
                return

            if target_message.author != interaction.client.user:
                await send_bad_argument(interaction, subtitle = {"message-id" : "This messages was not sent by me, so I cant edit it."})
                return
            _ = await target_message.edit(content = text)
            await interaction.followup.send("Edited!", ephemeral = True)

        except discord.Forbidden:
            _ = await send_unknown_error(interaction)
            return

    if await emoji_inaccessible(interaction, text, do_edit):
        return

    await do_edit(interaction)
