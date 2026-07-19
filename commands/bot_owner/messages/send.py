from asyncio import sleep

from discord import Forbidden, HTTPException, Message, NotFound
from discord.abc import Messageable

from bot import Interaction
from commands.bot_owner._base import TextChannelTypes, emoji_inaccessible
from core.exceptions import send_bad_argument, send_unknown_error

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner message send Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_send(
    interaction : Interaction,
    text        : str,
    reply_id    : str         | None = None,
    channel     : Messageable | None = None,
    *,
    ping        : bool        | None = True,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if ping is None:
        ping = True

    target_channel = channel or interaction.channel

    if not isinstance(target_channel, TextChannelTypes):
        await send_bad_argument(
            interaction,
            subtitle = {"channel" : "The selected channel does not support text messages."},
        )
        return

    async def do_send(interaction : Interaction) -> None:
        typing_speed = len(text) * 0.05
        typing_delay = min(typing_speed, 10.0)

        try:
            reply_reference : Message | None = None
            if reply_id:
                try:
                    reply_reference = await target_channel.fetch_message(int(reply_id))

                except (NotFound, ValueError, HTTPException):
                    await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist, I lack permissions to access it, or it is not a valid ID."})
                    return

            if hasattr(target_channel, "typing"):
                async with target_channel.typing():
                    await sleep(typing_delay)
            if reply_reference:
                await reply_reference.reply(text, mention_author = ping)
            else:
                await target_channel.send(text)
            await interaction.followup.send("Sent!", ephemeral = True)

        except Forbidden:
            await send_unknown_error(interaction)
            return

    if await emoji_inaccessible(interaction, text, do_send):
        return

    await do_send(interaction)
