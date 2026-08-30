from typing import Self, final, override

from discord import Member, Message

from bot import Interaction
from bot.types import GuildMessagable
from bot.ui import Checkbox, Label, Modal, TextDisplay, TextInput, UserSelect
from constants import CONTESTED_EMOJI
from core.exceptions import send_bad_argument
from core.responses import format_send
from core.utilities import check_hierarchy

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation purge Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_primary_purge(interaction : Interaction) -> None:
    @final
    class PurgeModal(Modal, title = "Purge Messages"):
        def __init__(self) -> None:
            super().__init__()

            self.text = TextDisplay[Self](
                (
                   f"{CONTESTED_EMOJI} **Use `Amount` alone, `Amount` + `Target`, or `Amount` + `Target` + `Force`.**\n"
                    "## Cases\n"
                    "### `Force = False (Default)`\n"
                    "Finds `n` messages from the channel and purges any from the target.\n"
                    "### `Force = True`\n"
                    "Finds `n` messages from the target and purges them from the channel."
                ),
            )

            self._amount = TextInput[Self](
                placeholder = 'ex: "10"',
                min_length  = 1,
                max_length  = 3,
            )
            self.amount  = Label[Self](
                text        = "Amount",
                description = "The amount of messages to purge.",
                component   = self._amount,
            )

            self._target = UserSelect[Self](placeholder = "Enter a member...", required = False)
            self.target  = Label[Self](
                text        = "Target",
                description = "The target to purge messages from.",
                component   = self._target,
            )

            self._force = Checkbox[Self](default = False)
            self.force  = Label[Self](
                text        = "Force",
                description = "Whether to force purge messages.",
                component   = self._force,
            )

            self.add_items(self.text, self.amount, self.target, self.force)

        @override
        async def on_submit(self, interaction : Interaction) -> None:
            target = self._target.values[0]
            force  = self._force.value

            await interaction.response.defer(ephemeral = True)

            # ⸻ We know that the command will run in a guild but the type checker doesn't...

            if not isinstance(interaction.user, Member) or not isinstance(target, Member):
                return

            # ⸻ We already validated interaction.channel.

            if not isinstance(interaction.channel, GuildMessagable):
                return

            # ⸻ Force requires Target.

            if force and not target:
                await send_bad_argument(
                    interaction,
                    subtitle = {"Force" : "`Force` is dependent on `Target`."},
                )
                return

            # ⸻ You cannot moderate yourself.

            if target == interaction.user:
                await send_bad_argument(
                    interaction,
                    subtitle = {"Target" : "You cannot moderate yourself."},
                )
                return

            # ⸻ You cannot moderate those higher in the hierarchy than you.

            if not check_hierarchy(
                actor      = interaction.user,
                target     = target,
                comparison = "<=",
            ):
                await send_bad_argument(
                    interaction,
                    subtitle = {"Target" : f"{target.mention} is higher in the hierarchy than you."},
                )
                return

            # ⸻ Validate amount.

            try:
                amount = int(self._amount.value)
            except ValueError, TypeError:
                await send_bad_argument(
                    interaction,
                    subtitle = {"Amount" : "`Amount` must be a valid whole number string."},
                )
                return

            match amount:
                case 0:
                    await send_bad_argument(
                        interaction,
                        subtitle = {"Amount" : "Cannot purge zero messages."},
                    )
                    return
                case 1:
                    await send_bad_argument(
                        interaction,
                        subtitle = {"Amount" : "Please delete the message manually."},
                    )
                    return
                case n if n < 0:
                    await send_bad_argument(
                        interaction,
                        subtitle = {"Amount" : "`Amount` cannot be a negative number."},
                    )
                    return
                case _:
                    pass

            # ⸻ Success!

            channel = interaction.channel

            # ~~~ TODO: Switch from raw logic to a proper BaseActions.purge call

            if not target:
                deleted = await channel.purge(limit = amount)
            elif not force:
                deleted = await channel.purge(
                    limit = amount,
                    check = lambda msg : msg.author == target,
                )
            else:
                messages : list[Message] = []

                async for message in channel.history(limit = 2000):
                    if message.author == target:
                        messages.append(message)
                        if len(messages) == amount:
                            break

                if messages:
                    message_set = set(messages)
                    deleted     = await channel.purge(
                        limit = 2000,
                        check = lambda msg : msg in message_set,
                    )
                else:
                    deleted = []

            await format_send(
                interaction,
                msg_type =  "success",
                title    =  "purged messages",
                subtitle = f"Purged {len(deleted)} messages.",
            )

    if not isinstance(interaction.channel, GuildMessagable):
        await send_bad_argument(
            interaction,
            subtitle = {None : "This channel is not purgable."},
        )
        return

    await interaction.response.send_modal(PurgeModal())
