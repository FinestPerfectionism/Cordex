import asyncio

import discord
from discord.abc import Messageable

from bot import Interaction
from commands.bot_owner._base import emoji_inaccessible
from core.exceptions import send_bad_argument, send_unknown_error

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner send Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_send(
    interaction : Interaction,
    channel     : Messageable,
    text        : str,
    message_id  : str | None = None,
) -> None:
    _ = await interaction.response.defer(ephemeral = True)

    async def do_send(interaction : Interaction) -> None:
        typing_speed = len(text) * 0.05
        typing_delay = min(typing_speed, 10.0)

        try:
            reply_reference : discord.Message | None = None
            if message_id:
                try:
                    if channel:
                        reply_reference = await channel.fetch_message(int(message_id))

                except (discord.NotFound, ValueError, discord.HTTPException):
                    await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist, I lack permissions to access it, or it is not a valid ID."})
                    return

            if hasattr(channel, "typing"):
                async with channel.typing():
                    await asyncio.sleep(typing_delay)
            if reply_reference:
                _ = await reply_reference.reply(content = text)
            else:
                _ = await channel.send(content = text)
            await interaction.followup.send("Sent!", ephemeral = True)

        except discord.Forbidden:
            _ = await send_unknown_error(interaction)
            return

    if await emoji_inaccessible(interaction, text, do_send):
        return

    await do_send(interaction)
