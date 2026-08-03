from typing import Self, final, override

from discord import Forbidden, HTTPException, Message, NotFound, TextStyle

from bot import Interaction
from bot.ui import Label, Modal, TextInput
from commands.bot_owner._base import TextChannelTypes, check_if_bo, emoji_inaccessible
from core.exceptions import send_bad_argument, send_bad_operation, send_unknown_error
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner message edit Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_edit(
    interaction : Interaction,
    text        : str,
    message_id  : str,
) -> None:
    await interaction.response.defer(ephemeral = True)

    channel = interaction.channel

    if not isinstance(channel, TextChannelTypes):
        await send_bad_argument(interaction, subtitle = {"channel" : "The current channel does not support text messages."})
        return

    async def do_edit(interaction : Interaction) -> None:
        try:
            try:
                target = await channel.fetch_message(int(message_id))

            except (NotFound, ValueError, HTTPException):
                await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist in this channel, I lack permissions to access it, or it is not a valid ID."})
                return

            if target.author != interaction.client.user:
                await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided was not sent by me, so I can't (and shouldn't) edit it."})
                return

            await target.edit(content = text)
            await interaction.followup.send("Edited!", ephemeral = True)

        except Forbidden:
            await send_unknown_error(interaction)
            return

    if await emoji_inaccessible(interaction, text, do_edit):
        return

    await do_edit(interaction)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Edit Message — Message Menu Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_messages_edit_menu(interaction : Interaction, message : Message) -> None:
    if not await check_if_bo(interaction):
        return

    if message.author != interaction.client.user:
        await send_bad_argument(interaction, subtitle = {None : "The message provided was not sent by me, so I can't (and shouldn't) edit it."})
        return

    @final
    class MessageModal(Modal, title = "Edit Message"):
        def __init__(self) -> None:
            super().__init__()
            self._text = TextInput[Self](
                style       = TextStyle.long,
                placeholder = "Type your updated message here...",
                default     = message.content,
                required    = True,
            )
            self.text  = Label[Self](
                text        = "Message",
                description = "The new text for the message.",
                component   = self._text,
            )

            self.add_item(self.text)

        @override
        async def on_submit(self, interaction : Interaction) -> None:
            try:
                await run_bo_messages_edit(
                    interaction,
                    text       = self._text.value,
                    message_id = str(message.id),
                )
            except Exception as e:
                await send_bad_operation(
                    interaction,
                    title    = "edit message",
                    subtitle = codeblock(f"{e}"),
                )

    try:
        await interaction.response.send_modal(MessageModal())
    except Exception as e:
        await send_bad_operation(
            interaction,
            title    = "edit message",
            subtitle = codeblock(f"{e}"),
        )
