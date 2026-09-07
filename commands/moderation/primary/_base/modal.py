from contextlib import suppress
from typing import Self, final, override

from discord import Member, User

from bot import Interaction
from bot.types import GuildMessagable
from bot.ui import (
    ActionRow,
    Button,
    Checkbox,
    Item,
    Label,
    LayoutView,
    Modal,
    TextDisplay,
    TextInput,
    VisibleLargeSeparator,
    button,
    grey,
    red,
)
from constants import ACCEPTED_EMOJI, CONTESTED_EMOJI, DENIED_EMOJI
from core.exceptions import send_bad_argument
from core.moderation import (
    Actions,
    ActionType,
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    PurgePayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)
from core.responses import ResponseOverride, format_message
from core.utilities import format_table

from .utilities import check_hierarchy

type Targetable = User | Member | GuildMessagable

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Select Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class ModerationModal(Modal):
    def __init__(
        self,
        action_type          : ActionType,
        target               : Targetable,
        *,
        reason_default       : str        | None = None,
        length_default       : str        | None = None,
        dtd_default          : str        | None = None,
        purge_target_default : Member     | None = None,
        amount_default       : str        | None = None,
        force_default        : bool              = False,
        dm_default           : bool              = False,
        edit_view            : LayoutView | None = None,
    ) -> None:
        self.edit_view            : LayoutView | None = edit_view
        self.purge_target_default : Member     | None = purge_target_default

        target_name = target.name

        member_types  = {
            "Ban Add",
            "Ban Remove",
            "Kick",
            "Quarantine Add",
            "Quarantine Remove",
            "Timeout Add",
            "Timeout Remove",
        }

        # ⸻ Validate that target is the correct type.

        if isinstance(target, GuildMessagable) and action_type != "Purge":
            error = "target cannot be GuildMessagable if action_type is not channel type"
            raise ValueError(error)

        if isinstance(target, Member | User) and action_type not in member_types:
            error = "target cannot be Member or User if action_type is not a user type"
            raise ValueError(error)

        title : dict[ActionType, str] = {
            "Ban Add"           : f"Banning {target_name}",
            "Ban Remove"        : f"Unbanning {target_name}",
            "Kick"              : f"Kicking {target_name}",
            "Quarantine Add"    : f"Placing {target_name} in Quarantine",
            "Quarantine Remove" : f"Removing {target_name} from Quarantine",
            "Timeout Add"       : f"Placing {target_name} in Timeout",
            "Timeout Remove"    : f"Removing {target_name} from Timeout",
            "Purge"             : f"Purging {target_name}",
        }
        name : dict[ActionType, str] = {
            "Ban Add"           : "ban",
            "Ban Remove"        : "ban removal",
            "Kick"              : "kick",
            "Quarantine Add"    : "quarantine",
            "Quarantine Remove" : "quarantine removal",
            "Timeout Add"       : "timeout",
            "Timeout Remove"    : "timeout removal",
            "Purge"             : "purge",
        }

        self.action_type : ActionType = action_type
        self.target                   = target
        self.name                     = name[action_type]

        super().__init__(title = title[action_type])

        items : list[Item[Self]] = []

        if action_type == "Purge":
            self.text = TextDisplay[Self](
               f"{CONTESTED_EMOJI} **Use `Amount` alone, `Amount` + `Target`, or `Amount` + `Target` + `Force`.**\n"
                "## Cases\n"
                "### `Force = False (Default)`\n"
                "Finds `n` messages from the channel and purges any from the target.\n"
                "### `Force = True`\n"
                "Finds `n` messages from the target and purges them from the channel.",
            )

            items.append(self.text)

        self._reason = TextInput[Self](placeholder = "Enter reason here...", default = reason_default)
        self.reason  = Label[Self](
            text        =  "Reason",
            description = f"Reason for the {self.name}.",
            component   = self._reason,
        )

        items.append(self.reason)

        if action_type == "Timeout Add":
            self._length = TextInput[Self](
                placeholder = "Enter length here...",
                required    = True,
                default     = length_default,
            )
            self.length  = Label[Self](
                text        = "Length",
                description = "Length of the timeout.",
                component   = self._length,
            )

            items.append(self.length)

        match action_type:
            case "Ban Add":
                self._dtd = TextInput[Self](
                    placeholder = "Enter number here...",
                    required    = False,
                    min_length  = 1,
                    max_length  = 1,
                    default     = dtd_default,
                )
                self.dtd  = Label[Self](
                    text        = "Days to Delete",
                    description = "Days to delete messages of the user upon ban. Defaults to 7.",
                    component   = self._dtd,
                )

                items.append(self.dtd)
            case "Purge":
                self._amount = TextInput[Self](
                    placeholder = 'ex: "10"',
                    min_length  = 1,
                    max_length  = 3,
                    default     = amount_default,
                )
                self.amount  = Label[Self](
                    text        = "Amount",
                    description = "The amount of messages to purge.",
                    component   = self._amount,
                )

                self._force = Checkbox[Self](default = force_default)
                self.force  = Label[Self](
                    text        = "Force",
                    description = "Whether to force purge messages.",
                    component   = self._force,
                )

                items.extend((self.amount, self.force))
            case _:
                pass

        if action_type != "Purge":
            self._dm = Checkbox[Self](default = dm_default)
            self.dm  = Label[Self](
                text        =  "DM",
                description = f"Whether to DM the user upon {self.name}. This can fail!",
                component   = self._dm,
            )

            items.append(self.dm)

        self.append_items(items)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        modal = self

        reason = self._reason.value

        length : str | None = None
        dtd    : str | None = None

        purge_member : Member | None = self.purge_target_default
        amount       : int    | None = None
        force        : bool          = False
        dm           : bool          = False

        if self.action_type == "Timeout Add":
            length = self._length.value

        await interaction.response.defer(ephemeral = True)

        match self.action_type:
            case "Ban Add":
                dtd = self._dtd.value
            case "Purge":
                force = self._force.value

                # ⸻ We know that the command will run in a guild but the type checker doesn't...

                if not interaction.guild or not isinstance(interaction.user, Member):
                    return

                # ⸻ We already validated that target is a GuildMessagable in __init__.

                if not isinstance(self.target, GuildMessagable):
                    return

                # ⸻ Force requires Target.

                if force and purge_member is None:
                    await send_bad_argument(
                        interaction,
                        subtitle = {"force" : "`force` is dependent on `target`."},
                    )
                    return

                # ⸻ Validate amount.

                try:
                    amount = int(self._amount.value)
                except ValueError, TypeError:
                    await send_bad_argument(
                        interaction,
                        subtitle = {"amount" : "`amount` must be a valid integer."},
                    )
                    return

                match amount:
                    case 0:
                        await send_bad_argument(
                            interaction,
                            subtitle = {"amount" : "Cannot purge zero messages."},
                        )
                        return
                    case 1:
                        await send_bad_argument(
                            interaction,
                            subtitle = {"amount" : "Please delete the message manually."},
                        )
                        return
                    case n if n < 0:
                        await send_bad_argument(
                            interaction,
                            subtitle = {"amount" : "`amount` cannot be a negative number."},
                        )
                        return
                    case _:
                        pass
            case _:
                pass

        if self.action_type != "Purge":
            dm = self._dm.value

        action_table : dict[str, object] = {"Reason" : reason}

        if length is not None:
            action_table["Length"] = length

        if dtd is not None:
            action_table["Days to Delete"] = dtd

        if self.action_type == "Purge":
            action_table["Amount"] = amount or "None"
            action_table["Force"]  = force

            sections : list[str] = [
                "### Target Channel",
                format_table(
                    {
                        "Channel"    : self.target.mention,
                        "Name"       : self.target.name,
                        "Channel ID" : self.target.id,
                    },
                ),
            ]

            if purge_member is not None:
                sections.extend(
                    (
                        "### Target Member",
                        format_table(
                            {
                                "User"     : purge_member.mention,
                                "Username" : purge_member.name,
                                "User ID"  : purge_member.id,
                            },
                        ),
                    ),
                )

            sections.extend(
                (
                    "### Action Information",
                    format_table(action_table),
                ),
            )

            summary = "\n".join(sections)
        else:
            action_table["DM Member"] = dm

            target_table : dict[str, object] = {
                "User"     : self.target.mention,
                "Username" : self.target.name,
                "User ID"  : self.target.id,
            } if isinstance(self.target, Member | User) else {
                "Channel"    : self.target.mention,
                "Name"       : self.target.name,
                "Channel ID" : self.target.id,
            }

            summary = (
                 "### Target\n"
                f"{format_table(target_table)}\n"
                 "### Action Information\n"
                f"{format_table(action_table)}"
            )

        class Edit(ActionRow["ModerationView"]):
            @button(label = "Edit", style = grey)
            async def btn_edit(self, interaction : Interaction, _button : Button[ModerationView]) -> None:
                view = self.view
                if not view:
                    return

                await interaction.response.send_modal(
                    ModerationModal(
                        modal.action_type,
                        modal.target,
                        reason_default       = reason,
                        length_default       = length,
                        dtd_default          = dtd,
                        purge_target_default = purge_member,
                        amount_default       = str(amount) if amount is not None else None,
                        force_default        = force,
                        dm_default           = dm,
                        edit_view            = view,
                    ),
                )

            @button(label = "Execute", style = red)
            async def btn_execute(self, interaction : Interaction, _button : Button[ModerationView]) -> None:
                await interaction.response.defer(ephemeral = True)

                guild = interaction.guild
                if not guild or not isinstance(interaction.user, Member):
                    return

                actions   = Actions(interaction.client, guild)
                moderator = interaction.user

                match modal.action_type:
                    case "Ban Add":
                        if not isinstance(modal.target, Member):
                            return

                        seconds_to_delete = 7 * 86400
                        if dtd is not None:
                            with suppress(ValueError):
                                seconds_to_delete = int(dtd) * 86400

                        result = await actions.ban_add(
                            BanAddPayload(
                                moderator         = moderator,
                                target            = modal.target,
                                reason            = reason,
                                dm_user           = dm,
                                seconds_to_delete = seconds_to_delete,
                            ),
                        )
                    case "Ban Remove":
                        if not isinstance(modal.target, Member):
                            return

                        result = await actions.ban_remove(
                            BanRemovePayload(
                                moderator = moderator,
                                target    = modal.target,
                                reason    = reason,
                                dm_user   = dm,
                            ),
                        )
                    case "Kick":
                        if not isinstance(modal.target, Member):
                            return

                        result = await actions.kick(
                            KickPayload(
                                moderator = moderator,
                                target    = modal.target,
                                reason    = reason,
                                dm_user   = dm,
                            ),
                        )
                    case "Quarantine Add":
                        if not isinstance(modal.target, Member):
                            return

                        result = await actions.quarantine_add(
                            QuarantineAddPayload(
                                moderator = moderator,
                                target    = modal.target,
                                reason    = reason,
                                dm_user   = dm,
                            ),
                        )
                    case "Quarantine Remove":
                        if not isinstance(modal.target, Member):
                            return

                        result = await actions.quarantine_remove(
                            QuarantineRemovePayload(
                                moderator = moderator,
                                target    = modal.target,
                                reason    = reason,
                                dm_user   = dm,
                            ),
                        )
                    case "Timeout Add":
                        if not isinstance(modal.target, Member):
                            return

                        try:
                            timeout_length = int(length) if length is not None else 0
                        except ValueError:
                            timeout_length = 0

                        result = await actions.timeout_add(
                            TimeoutAddPayload(
                                moderator = moderator,
                                target    = modal.target,
                                reason    = reason,
                                dm_user   = dm,
                                length    = timeout_length,
                            ),
                        )
                    case "Timeout Remove":
                        if not isinstance(modal.target, Member):
                            return

                        result = await actions.timeout_remove(
                            TimeoutRemovePayload(
                                moderator = moderator,
                                target    = modal.target,
                                reason    = reason,
                                dm_user   = dm,
                            ),
                        )
                    case "Purge":
                        if not isinstance(modal.target, GuildMessagable):
                            return

                        result = await actions.purge(
                            PurgePayload(
                                moderator = moderator,
                                target    = purge_member,
                                reason    = reason,
                                channel   = modal.target,
                                amount    = amount or 0,
                                force     = force,
                            ),
                        )

                table : dict[str, str] = {}
                statuses : list[bool] = []

                if not result.failed:
                    table[modal.action_type] = f"{ACCEPTED_EMOJI} Success."
                    statuses.append(True)
                else:
                    table[modal.action_type] = f"{DENIED_EMOJI} Fail."
                    statuses.append(False)

                if result.dmed is True:
                    table["DMed Member"] = f"{ACCEPTED_EMOJI} Success."
                    statuses.append(True)
                elif result.dmed is False:
                    table["DMed Member"] = f"{DENIED_EMOJI} Fail."
                    statuses.append(False)

                # if result.logged is True:
                #     table["Logged"] = f"{ACCEPTED_EMOJI} Success."
                #     statuses.append(True)
                # elif result.logged is False:
                #     table["Logged"] = f"{DENIED_EMOJI} Fail."
                #     statuses.append(False)

                if modal.action_type == "Purge" and isinstance(result.data, int):
                    purge_line = f"Purged {result.data} message(s).\n"
                else:
                    purge_line = None

                subtitle = (
                    f"{purge_line}"
                    f"{format_table(table)}"
                )

                if all(statuses):
                    msg_type = "success"
                elif any(statuses):
                    msg_type = "warning"
                else:
                    msg_type = "error"

                if all(statuses):
                    title = f"The {modal.name} was successful"
                elif any(statuses):
                    title = f"The {modal.name} was partially successful"
                else:
                    title = f"The {modal.name} failed"

                result_view = LayoutView()
                result_view.add_item(
                    TextDisplay(
                        format_message(
                            msg_type = msg_type,
                            title    = title,
                            subtitle = subtitle,
                            override = ResponseOverride(prefix = False),
                        ),
                    ),
                )

                await interaction.edit_original_response(view = result_view)

        class ModerationView(LayoutView):
            def __init__(self) -> None:
                super().__init__()
                self.add_items(
                    TextDisplay(summary),
                    VisibleLargeSeparator(),
                    Edit(),
                )

        view = ModerationView()

        if self.edit_view:
            await interaction.edit_original_response(view = view)
        else:
            await interaction.followup.send(view = view, ephemeral = True)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# send_moderation_modal
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_moderation_modal(
    interaction  : Interaction,
    action_type  : ActionType,
    target       : Targetable,
    purge_target : Member | None = None,
) -> None:
    client = interaction.client
    user   = interaction.user

    if not interaction.guild or not isinstance(user, Member):
        return

    check_target = purge_target if action_type == "Purge" else target

    if isinstance(check_target, Member):

        # ⸻ You cannot moderate yourself.

        if check_target == interaction.user:
            await send_bad_argument(
                interaction,
                subtitle = {"target" : "You cannot moderate yourself."},
            )
            return

        if not check_hierarchy(user, ">", check_target):
            if check_hierarchy(user, "=", check_target):
                if check_target == client.user:
                    await send_bad_argument(
                        interaction,
                        subtitle = {"target" : f"{check_target.mention} is equal to you in the hierarchy."},
                        footer   = "Nice try",
                    )
                    return

                await send_bad_argument(
                    interaction,
                    subtitle = {"target" : f"{check_target.mention} is equal to you in the hierarchy."},
                )
                return

            if check_target == client.user:
                await send_bad_argument(
                    interaction,
                    subtitle = {"target" : f"{check_target.mention} is higher in the hierarchy than you."},
                    footer   = "Nice try",
                )
                return

            await send_bad_argument(
                interaction,
                subtitle = {"target" : f"{check_target.mention} is higher in the hierarchy than you."},
            )
            return
        if check_target == client.user:
            await send_bad_argument(
                interaction,
                subtitle = {"target" : f"{check_target.mention} cannot be moderated."},
            )
            return

    action_types = {
        "Ban Add",
        "Ban Remove",
        "Kick",
        "Quarantine Add",
        "Quarantine Remove",
        "Timeout Add",
        "Timeout Remove",
        "Purge",
    }

    if action_type not in action_types:
        error = f"action_type '{action_type}' is not a recognized moderation action"
        raise ValueError(error)

    modal = ModerationModal(action_type, target, purge_target_default = purge_target)

    await interaction.response.send_modal(modal)
