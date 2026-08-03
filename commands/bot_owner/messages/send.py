from asyncio import sleep
from typing import Self, final, override

from discord import Forbidden, HTTPException, Message, NotFound, TextStyle

from bot import Interaction
from bot.ui import Checkbox, Label, Modal, TextInput
from commands.bot_owner._base import TextChannelTypes, check_if_bo, emoji_inaccessible
from core.exceptions import send_bad_argument, send_bad_operation, send_unknown_error
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner message send Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_send(
    interaction : Interaction,
    text        : str,
    reply_id    : str  | None = None,
    *,
    ping        : bool | None = True,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if ping is None:
        ping = True

    channel = interaction.channel

    if not isinstance(channel, TextChannelTypes):
        await send_bad_argument(
            interaction,
            subtitle = {"channel" : "The current channel does not support text messages."},
        )
        return

    async def do_send(interaction : Interaction) -> None:
        typing_speed = len(text) * 0.05
        typing_delay = min(typing_speed, 10.0)

        try:
            reference : Message | None = None
            if reply_id:
                try:
                    reference = await channel.fetch_message(int(reply_id))

                except (NotFound, ValueError, HTTPException):
                    await send_bad_argument(
                        interaction,
                        subtitle = {"message-id" : "The message provided does not exist in this channel, I lack permissions to access it, or it is not a valid ID."},
                    )
                    return

            if hasattr(channel, "typing"):
                async with channel.typing():
                    await sleep(typing_delay)
            if reference:
                await reference.reply(text, mention_author = ping)
            else:
                await channel.send(text)
            await interaction.followup.send("Sent!", ephemeral = True)

        except Forbidden:
            await send_unknown_error(interaction)
            return

    if await emoji_inaccessible(interaction, text, do_send):
        return

    await do_send(interaction)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Reply to Message — Message Menu Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_reply_menu(interaction : Interaction, message : Message) -> None:
    if not await check_if_bo(interaction):
        return

    @final
    class MessageModal(Modal, title = "Reply to Message"):
        def __init__(self) -> None:
            super().__init__()
            self._ping = Checkbox[Self](default = True)
            self.ping  = Label[Self](
                text        = "Mention Author",
                description = "Whether to mention the user.",
                component   = self._ping,
            )

            self._text = TextInput[Self](
                style       = TextStyle.long,
                placeholder = "Type your message here...",
                required    = True,
            )
            self.text  = Label[Self](
                text        = "Message",
                description = "The text to reply with.",
                component   = self._text,
            )

            self.add_item(self.ping)
            self.add_item(self.text)

        @override
        async def on_submit(self, interaction : Interaction) -> None:
            try:
                await run_bo_messages_send(
                    interaction,
                    text     = self._text.value,
                    reply_id = str(message.id),
                    ping     = self._ping.value,
                )
            except Exception as e:
                await send_bad_operation(
                    interaction,
                    title    = "reply to message",
                    subtitle = codeblock(f"{e}"),
                )

    try:
        await interaction.response.send_modal(MessageModal())
    except Exception as e:
        await send_bad_operation(
            interaction,
            title    = "reply to message",
            subtitle = codeblock(f"{e}"),
        )
