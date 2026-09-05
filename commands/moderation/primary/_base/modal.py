from typing import Self, final, override

from discord import Member

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
    UserSelect,
    VisibleLargeSeparator,
    button,
    grey,
    red,
)
from constants import CONTESTED_EMOJI
from core.exceptions import send_bad_argument
from core.moderation import ActionType
from core.utilities import check_hierarchy, format_table

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
        action_type      : ActionType,
        target           : Member | GuildMessagable,
        *,
        reason_default   : str    | None = None,
        length_default   : str    | None = None,
        dtd_default      : str    | None = None,
        memberid_default : str    | None = None,
        purge_default    : Member | None = None,
        amount_default   : str    | None = None,
        force_default    : bool          = False,
        dm_default       : bool          = False,
    ) -> None:
        target_name = target.name

        channel_types = {"Purge"}
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

        if isinstance(target, GuildMessagable) and action_type not in channel_types:
            error = "target cannot be GuildMesseagable if action_type is not channel type"
            raise ValueError(error)

        if isinstance(target, Member) and action_type not in member_types:
            error = "target cannot be Member if action_type is not a member type"
            raise ValueError(error)

        title : dict[ActionType, str] = {
            "Ban Add"           : f"Banning {target_name}",
            "Ban Remove"        :  "Unbanning a Member",
            "Kick"              : f"Kick {target_name}",
            "Quarantine Add"    : f"Place {target_name} in Quarantine",
            "Quarantine Remove" : f"Remove {target_name} from Quarantine",
            "Timeout Add"       : f"Place {target_name} in Timeout",
            "Timeout Remove"    : f"Remove {target_name} from Timeout",
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
                (
                   f"{CONTESTED_EMOJI} **Use `Amount` alone, `Amount` + `Target`, or `Amount` + `Target` + `Force`.**\n"
                    "## Cases\n"
                    "### `Force = False (Default)`\n"
                    "Finds `n` messages from the channel and purges any from the target.\n"
                    "### `Force = True`\n"
                    "Finds `n` messages from the target and purges them from the channel."
                ),
            )

            items.append(self.text)

        self._reason = TextInput[Self](placeholder = "Enter reason here...", default = reason_default)
        self.reason  = Label[Self](
            text        =  "Reason",
            description = f"Reason for the {self.name}.",
            component   = self._reason,
        )

        items.append(self.reason)

        is_lengthable = action_type.endswith("Add")
        if is_lengthable:
            is_permanent     = (action_type == "Ban Add")
            length_statement = " Defaults to permanent." if is_permanent else ""

            self._length = TextInput[Self](
                placeholder = "Enter length here...",
                required    = not is_permanent,
                default     = length_default,
            )
            self.length  = Label[Self](
                text        =  "Length",
                description = f"Length of the {self.name}.{length_statement}",
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
            case "Ban Remove":
                self._memberid = TextInput[Self](placeholder = "Enter ID here...", default = memberid_default)
                self.memberid  = Label[Self](
                    text        = "Member ID",
                    description = "ID of the member to unban.",
                    component   = self._memberid,
                )

                items.append(self.memberid)
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

                self._purge_target = UserSelect[Self](
                    placeholder    = "Enter a member...",
                    required       = False,
                    default_values = [purge_default] if purge_default else [],
                )
                self.purge_target  = Label[Self](
                    text        = "Target",
                    description = "The target to purge messages from.",
                    component   = self._purge_target,
                )

                self._force = Checkbox[Self](default = force_default)
                self.force  = Label[Self](
                    text        = "Force",
                    description = "Whether to force purge messages.",
                    component   = self._force,
                )

                items.extend((self.amount, self.purge_target, self.force))
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

        length   : str | None = None
        dtd      : str | None = None
        memberid : str | None = None

        purge_member : Member | None = None
        amount       : int    | None = None
        force        : bool          = False
        dm           : bool          = False

        if self.action_type.endswith("Add"):
            length = self._length.value

        await interaction.response.defer(ephemeral = True)

        match self.action_type:
            case "Ban Add":
                dtd = self._dtd.value
            case "Ban Remove":
                memberid = self._memberid.value
            case "Purge":
                force          = self._force.value
                selected_users = self._purge_target.values
                target_user    = selected_users[0] if selected_users else None
                purge_member   = target_user if isinstance(target_user, Member) else None

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
                        subtitle = {"Force" : "`Force` is dependent on `Target`."},
                    )
                    return

                if purge_member is not None:

                    # ⸻ You cannot moderate yourself.

                    if purge_member == interaction.user:
                        await send_bad_argument(
                            interaction,
                            subtitle = {"Target" : "You cannot moderate yourself."},
                        )
                        return

                    # ⸻ You cannot moderate those higher in the hierarchy than you.

                    if not check_hierarchy(
                        actor      = interaction.user,
                        target     = purge_member,
                        comparison = "<=",
                    ):
                        await send_bad_argument(
                            interaction,
                            subtitle = {"Target" : f"{purge_member.mention} is higher in the hierarchy than you."},
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
            case _:
                pass

        if self.action_type != "Purge":
            dm = self._dm.value

        target_table : dict[str, object] = {
            "User"     : self.target.mention,
            "Username" : self.target.name,
            "User ID"  : self.target.id,
        } if isinstance(self.target, Member) else {
            "Channel"    : self.target.mention,
            "Name"       : self.target.name,
            "Channel ID" : self.target.id,
        }

        action_table : dict[str, object] = {"Reason": reason}

        if length is not None:
            action_table["Length"] = length

        if dtd is not None:
            action_table["Days to Delete"] = dtd

        if memberid is not None:
            action_table["Member ID"] = memberid

        if self.action_type == "Purge":
            action_table["Target"] = purge_member.mention if purge_member else "None"
            action_table["Amount"] = amount if amount is not None else "None"
            action_table["Force"]  = force
        else:
            action_table["DM Member"] = dm

        summary = (
             "### Target\n"
            f"{format_table(target_table)}\n"
             "### Action Information\n"
            f"{format_table(action_table)}"
        )

        class Edit(ActionRow["ModerationView"]):
            @button(label = "Edit", style = grey)
            async def btn_edit(self, interaction : Interaction, _button : Button[ModerationView]) -> None:
                await interaction.response.send_modal(
                    ModerationModal(
                        modal.action_type,
                        modal.target,
                        reason_default   = reason,
                        length_default   = length,
                        dtd_default      = dtd,
                        memberid_default = memberid,
                        purge_default    = purge_member,
                        amount_default   = str(amount) if amount is not None else None,
                        force_default    = force,
                        dm_default       = dm,
                    ),
                )

            @button(label = "Execute", style = red)
            async def btn_execute(self, _interaction : Interaction, _button : Button[ModerationView]) -> None:
                ...

        class ModerationView(LayoutView):
            def __init__(self) -> None:
                super().__init__()
                self.add_items(
                    TextDisplay(summary),
                    VisibleLargeSeparator(),
                    Edit(),
                )

        await interaction.followup.send(view = ModerationView(), ephemeral = True)
