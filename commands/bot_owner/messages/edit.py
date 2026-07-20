from discord import Forbidden, HTTPException, NotFound
from discord.abc import Messageable

from bot import Interaction
from commands.bot_owner._base import TextChannelTypes, emoji_inaccessible
from core.exceptions import send_bad_argument, send_unknown_error

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner message edit Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_edit(
    interaction : Interaction,
    text        : str,
    message_id  : str,
    channel     : Messageable | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    target_channel = channel or interaction.channel

    if not isinstance(target_channel, TextChannelTypes):
        await send_bad_argument(interaction, subtitle = {"channel" : "The selected channel does not support text messages."})
        return

    async def do_edit(interaction : Interaction) -> None:
        try:
            try:
                target_message = await target_channel.fetch_message(int(message_id))

            except (NotFound, ValueError, HTTPException):
                await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist, I lack permissions to access it, or it is not a valid ID."})
                return

            if target_message.author != interaction.client.user:
                await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided was not sent by me, so I can't (and shouldn't) edit it."})
                return

            await target_message.edit(content = text)
            await interaction.followup.send("Edited!", ephemeral = True)

        except Forbidden:
            await send_unknown_error(interaction)
            return

    if await emoji_inaccessible(interaction, text, do_edit):
        return

    await do_edit(interaction)
