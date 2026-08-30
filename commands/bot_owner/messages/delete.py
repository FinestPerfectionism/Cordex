from typing import TYPE_CHECKING

from discord import Forbidden, HTTPException, Message, NotFound
from discord.abc import Messageable

from commands.bot_owner._base import check_if_bo
from core.exceptions import send_bad_argument, send_bad_operation, send_unknown_error
from core.utilities import codeblock

if TYPE_CHECKING:
    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner message delete Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_delete(interaction : Interaction, message_id : str) -> None:
    await interaction.response.defer(ephemeral = True)

    channel = interaction.channel

    if not isinstance(channel, Messageable):
        await send_bad_argument(interaction, subtitle = {"channel" : "The current channel does not support text messages."})
        return

    try:
        try:
            target = await channel.fetch_message(int(message_id))
        except (NotFound, ValueError, HTTPException):
            await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist in this channel, I lack permissions to access it, or it is not a valid ID."})
            return

        if target.author != interaction.client.user:
            await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided was not sent by me, so I shouldn't delete it."})
            return

        await target.delete()
        await interaction.followup.send("Deleted!", ephemeral = True)

    except Forbidden:
        await send_unknown_error(interaction)
        return

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# 'Delete Message' Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_delete_menu(interaction : Interaction, message : Message) -> None:
    if not await check_if_bo(interaction):
        return

    if message.author != interaction.client.user:
        await send_bad_argument(interaction, subtitle = {None : "The message provided was not sent by me, so I shouldn't delete it."})
        return

    try:
        await run_bo_messages_delete(interaction, message_id = str(message.id))
    except Exception as e:
        await send_bad_operation(
            interaction,
            title    = "delete message",
            subtitle = codeblock(f"{e}"),
        )
