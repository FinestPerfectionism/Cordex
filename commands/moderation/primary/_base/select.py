from collections.abc import Sequence
from re import match
from typing import Literal, Self, TypedDict, final, override

from discord import AllowedMentions, ButtonStyle, Member
from discord.ui import (
    ActionRow,
    Button,
    Checkbox,
    FileUpload,
    Label,
    Modal,
    TextDisplay,
    TextInput,
    UserSelect,
    View,
    select,
)
from discord.utils import escape_markdown

from bot import Interaction
from bot.ui import (
    ButtonSection,
    Container,
    LayoutView,
    VisibleLargeSeparator,
    blurple,
    green,
    grey,
    red,
)
from constants import ACCEPTED_EMOJI
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import format_send
from core.utilities import check_hierarchy, format_table, format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Select Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

ActionType = Literal[
    "Ban Add",
    "Ban Remove",
    "Kick",
    "Quarantine Add",
    "Quarantine Remove",
    "Timeout Add",
    "Timeout Remove",
]

class _StateEntry(TypedDict, total = False):
    reason     : str
    length     : str
    appealable : bool
    dm_user    : bool
    file       : str | None


type _StateMap = dict[int, _StateEntry]

def _build_member_label(member : Member, state : _StateEntry | None) -> str:
    if not state:
        return member.mention

    reason = escape_markdown(str(state.get("reason", "")))

    table_data = {
        "Reason"     : f'"{reason}"',
        "Length"     : f"{state.get("length", "N/A")}",
        "Appealable" : f"{state.get("appealable", False)}",
        "DM"         : f"{state.get("dm_user", False)}",
    }

    if "file" in state:
        table_data["File"] = f"{state["file"]}"

    return (
        f"{member.mention}\n"
        f"{format_table(table_data)}"
    )

def _resolve_state(
    member       : Member,
    state_map    : _StateMap,
    global_state : _StateEntry | None,
) -> _StateEntry | None:
    return state_map.get(member.id) or global_state

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# _ActionButton
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class _ActionButton(Button[LayoutView]):
    def __init__(
        self,
        action_type : ActionType,
        target      : Member | None,
        editor      : "_EditorView",
        *,
        style       : ButtonStyle   = grey,
        label       : str    | None = None,
    ) -> None:
        super().__init__(style = style, label = label)
        self.action_type : ActionType    = action_type
        self.target      : Member | None = target
        self.editor      : "_EditorView" = editor

    @override
    async def callback(self, interaction : Interaction) -> None:
        try:
            await interaction.response.send_modal(_ReasonModal(self.action_type, self.target, self.editor))
        except Exception:
            await send_bad_operation(interaction, title = "open modal")
            raise

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# _ReasonModal
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _ReasonModal(Modal):
    def __init__(
        self,
        action_type : ActionType,
        target      : Member | None,
        editor      : "_EditorView",
    ) -> None:
        super().__init__(title = f"Reason: {target.name}" if target else "Global Action")
        self.target = target
        self.editor = editor

        existing : _StateEntry = editor.state_map.get(
            target.id if target else 0,
            editor.state_map.get(0, {}),
        )

        self.reason_input : TextInput[Modal] = TextInput[Modal](
            label       = "Reason",
            placeholder = 'ex: "nsfw spam"',
            default     = str(existing.get("reason", "")),
            required    = True,
        )
        self.length_input : TextInput[Modal] = TextInput[Modal](
            label       = "Length",
            placeholder = 'ex: "30m, 2d"',
            default     = str(existing.get("length", "")),
            required    = True,
        )
        self.appealable_checkbox : Checkbox[Modal]   = Checkbox(default = bool(existing.get("appealable", False)))
        self.dm_checkbox         : Checkbox[Modal]   = Checkbox(default = bool(existing.get("dm_user",    False)))
        self.proof_fileupload    : FileUpload[Modal] = FileUpload(required = False, max_values = 1)

        for item in [
            self.reason_input,
            self.length_input,
            Label(
                text        = "Appealable",
                description = "Whether the action is appealable. *DM must be set to true for the action to be appealable!",
                component   = self.appealable_checkbox,
            ),
            Label(
                text        = "DM",
                description = "Whether to DM the user.",
                component   = self.dm_checkbox,
            ),
            Label(
                text        = "Proof",
                description = "Upload a file as proof.",
                component   = self.proof_fileupload,
            ),
        ]:
            self.add_item(item)

    @override
    async def on_submit(self, interaction : Interaction) -> None:

        # ⸻ You cannot make an action appealable without DMing the user

        if self.appealable_checkbox.value and not self.dm_checkbox.value:
            await format_send(
                interaction,
                msg_type = "warning",
                title    = "compile window",
                subtitle = "You cannot make an action appealable without DMing the user.",
            )
            return

        # ⸻ Improper time signature

        length_value = self.length_input.value.strip().lower()
        if length_value and not match(r"^(\d+[hmds])+$", length_value):
            await format_send(
                interaction,
                msg_type =  "warning",
                title    =  "compile window",
                subtitle = f"The time signature `{self.length_input.value}` is not valid. Use formats like 10m, 2h, 1d.",
            )
            return

        if (user_id := self.target.id if self.target else 0) == 0:
            self.editor.state_map.clear()

        filename : str | None = next(
            (f.filename for f in self.proof_fileupload.values),
            None,
        )
        self.editor.state_map[user_id] = {
            "reason"     : self.reason_input.value,
            "length"     : self.length_input.value,
            "appealable" : self.appealable_checkbox.value,
            "dm_user"    : self.dm_checkbox.value,
            "file"       : filename,
        }
        await self.editor.refresh(interaction)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# _EditorView
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _EditorView(LayoutView):
    def __init__(
        self,
        action_type : ActionType,
        members     : Sequence[Member] | None = None,
    ) -> None:
        super().__init__(timeout = None)
        self.action_type : ActionType = action_type
        self.members                  = list(members) if members else []
        self.state_map   : _StateMap  = {}
        self.rebuild()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # rebuild
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def rebuild(self) -> None:
        self.clear_items()
        container : Container = Container()
        global_state          = self.state_map.get(0)

        for member in self.members:
            resolved = _resolve_state(member, self.state_map, global_state)
            label    = _build_member_label(member, resolved)

            if resolved:
                style = green if (member.id in self.state_map or 0 in self.state_map) else blurple
            else:
                style = grey

            button = _ActionButton(self.action_type, member, self, style = style, label = "Action")
            container.add_item(ButtonSection(label, button = button))
        container.add_item(VisibleLargeSeparator())

        async def handle_execute(interaction : Interaction) -> None:
            errors : list[str] = []
            global_entry       = self.state_map.get(0)

            for member in self.members:
                entry               = _resolve_state(member, self.state_map, global_entry)
                missing : list[str] = []
                if not entry or not entry.get("reason"):
                    missing.append("reason")
                if not entry or not entry.get("length"):
                    missing.append("timer")
                if missing:
                    errors.append(f"- {member.mention}: Missing {format_values(missing)}")

            if errors:
                try:
                    await format_send(
                        interaction,
                        msg_type  = "warning",
                        title     = "moderate members",
                        subtitle  = (
                            "Fix the following assignments before executing:\n"
                            + "\n".join(errors)
                        ),
                    )
                except Exception:
                    await send_bad_operation(interaction, title = "compile window")
                    raise
                return

            try:
                summary_lines = [f"**{ACCEPTED_EMOJI} Successfully mass moderated all members.**"]

                for member in self.members:
                    entry = _resolve_state(member, self.state_map, global_entry)

                    if entry:
                        reason     = escape_markdown(entry.get("reason", "N/A"))
                        length     = entry.get("length", "N/A")
                        appealable = "Yes" if entry.get("appealable") else "No"
                        dm_user    = "Yes" if entry.get("dm_user")    else "No"
                        file       = escape_markdown(entry.get("file") or "None")

                        summary_lines.append(
                            (
                                f"{member.mention}\n"
                                f"`     Reason:` {reason}\n"
                                f"`     Length:` {length}\n"
                                f"` Appealable:` {appealable} | `DM Sent:` {dm_user}\n"
                                f"` Attachment:` {file}"
                            ),
                        )

                    else:
                        summary_lines.append(
                            (
                               f"### Partial success for {member.mention}.\n"
                                "-# Missing configuration data for this member."
                            ),
                        )

                class FinalizedView(LayoutView):
                    text : TextDisplay[Self] = TextDisplay("\n".join(summary_lines))
                await interaction.response.edit_message(view = FinalizedView())

            except Exception:
                await send_bad_operation(interaction, title = "compile window")
                raise

        execute_button : Button[LayoutView] = Button(style = red, label = "Execute")
        execute_button.callback             = handle_execute

        container.add_item(
            ActionRow(
                _ActionButton(
                    self.action_type,
                    None,
                    self,
                    style = blurple,
                    label = "Global",
                ),
                execute_button,
            ),
        )
        self.add_item(container)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # refresh
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def refresh(self, interaction : Interaction) -> None:
        self.rebuild()
        try:
            await interaction.response.edit_message(
                view             = self,
                allowed_mentions = AllowedMentions.none(),
            )
        except Exception:
            await send_bad_operation(interaction, title = "compile window")
            raise

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# MemberSelectView
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MemberSelectView(View):
    type_map : dict[ActionType, str] = {
        "Ban Add"           : "Select members to ban...",
        "Ban Remove"        : "Select members to un-ban...",
        "Kick"              : "Select members to kick...",
        "Quarantine Add"    : "Select members to place in quarantine...",
        "Quarantine Remove" : "Select members to remove from quarantine...",
        "Timeout Add"       : "Select members to place in timeout...",
        "Timeout Remove"    : "Select members to remove from timeout...",
    }

    current_action : ActionType = "Ban Add"

    placeholder = type_map[current_action]

    def __init__(self, action_type : ActionType) -> None:
        super().__init__(timeout = None)
        self.action_type : ActionType = action_type

    @select(cls = UserSelect, placeholder = placeholder, max_values = 1)
    async def slct_moderation_members(
        self,
        interaction : Interaction,
        select      : UserSelect[Self],
    ) -> None:
        chosen_members = select.values
        guild = interaction.guild

        # ⸻ We know that the command will run in a guild but the type checker doesn't...

        if not guild or not isinstance(interaction.user, Member):
            return

        # ⸻ You cannot moderate me... maybe?

        if guild.me in chosen_members:
            if len(chosen_members) == 1:
                if interaction.user == guild.owner:
                    await send_bad_argument(
                        interaction,
                        subtitle = {None : "Please... spare me... 😭"},
                        footer   = "Use the native discord `/kick` or `/ban` command to remove me from the guild...",
                    )
                    return

                ineligible = check_hierarchy(interaction.user, guild.me, "<=")
                msg    = f"The user {guild.me.mention} is higher in the hierarchy than you." if ineligible else "Please... spare me... 😭"
                footer =  "Nice try" if ineligible else "Use the native discord /kick or /ban command to remove me from the guild..."

                await send_bad_argument(
                    interaction,
                    subtitle = {None : msg},
                    footer   = footer,
                )
                return

            other_members = [m for m in chosen_members if m != guild.me]
            mentions = [m.mention for m in other_members]

            word_user = "user" if len(mentions) == 1 else "users"
            word_is   = "is"   if len(mentions) == 1 else "are"

            await send_bad_argument(
                interaction,
                subtitle = {None : f"The {word_user} {format_values(mentions)} {word_is} higher in the hierarchy than you; {guild.me.mention} is unmoderatable."},
                footer   = "Bad argument. Use the native discord /kick or /ban command to remove me from the guild...",
            )
            return

        # ⸻ You cannot moderate yourself

        if interaction.user in chosen_members:
            await send_bad_argument(
                interaction,
                subtitle = {None : "You cannot moderate yourself."},
            )
            return

        # ⸻ You cannot moderate those higher in the hierarchy than you

        ineligible = [
            member.mention for member in chosen_members
            if isinstance(member, Member)
            and check_hierarchy(interaction.user, member, "<=")
        ]

        if ineligible:
            word_user = "user" if len(ineligible) == 1 else "users"
            word_is   = "is"   if len(ineligible) == 1 else "are"

            await send_bad_argument(
                interaction,
                subtitle = {None : f"The {word_user} {format_values(ineligible)} {word_is} higher in the hierarchy than you."},
            )
            return

        # ⸻ Final try

        members = [user for user in select.values if isinstance(user, Member)]

        try:
            await interaction.response.edit_message(view = _EditorView(self.action_type, members = members))
        except Exception:
            await send_bad_operation(interaction, title = "compile window")
            raise
