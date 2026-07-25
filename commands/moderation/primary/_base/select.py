from collections.abc import Sequence
from re import match
from types import MappingProxyType
from typing import Literal, Self, TypedDict, cast, final, override

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

_REMOVAL_TYPES = frozenset(
    {
        "Ban Remove",
        "Quarantine Remove",
        "Timeout Remove",
    },
)
_LENGTH_TYPES  = frozenset(
    {
        "Ban Add",
        "Quarantine Add",
        "Timeout Add",
    },
)

def _wants_length(action_type : ActionType) -> bool:
    return action_type in _LENGTH_TYPES

def _wants_extra(action_type : ActionType) -> bool:
    return action_type not in _REMOVAL_TYPES and action_type != "Kick"

class _StateEntry(TypedDict, total = False):
    reason     : str
    length     : str
    appealable : bool
    dm_user    : bool
    file       : str | None


type _StateMap = dict[int, _StateEntry]

def _build_member_label(member : Member, state : _StateEntry | None, action_type : ActionType) -> str:
    if not state:
        return member.mention

    reason = escape_markdown(str(state.get("reason", "")))

    table_data : dict[str, str] = {"Reason" : f'"{reason}"'}

    if _wants_length(action_type):
        table_data["Length"] = str(state.get("length", "N/A"))

    if _wants_extra(action_type):
        table_data["Appealable"] = str(state.get("appealable", False))

    table_data["DM"] = str(state.get("dm_user", False))

    if "file" in state:
        table_data["File"] = str(state["file"])

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

@final
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
        self.action_type : ActionType = action_type
        self.target                   = target
        self.editor                   = editor

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
        self.target      = target
        self.editor      = editor
        self.action_type = action_type

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
        self.dm_checkbox : Checkbox[Modal] = Checkbox(default = bool(existing.get("dm_user", False)))

        self.length_input        : TextInput[Modal]  | None = None
        self.appealable_checkbox : Checkbox[Modal]   | None = None
        self.proof_fileupload    : FileUpload[Modal] | None = None

        if _wants_length(action_type):
            self.length_input = TextInput[Modal](
                label       = "Length",
                placeholder = 'ex: "30m, 2d"' if action_type == "Timeout Add" else 'ex: "30m, 2d" — Permanant if empty',
                default     = str(existing.get("length", "")),
                required    = (action_type == "Timeout Add"),
            )

        if _wants_extra(action_type):
            self.appealable_checkbox = Checkbox(default = bool(existing.get("appealable", False)))
            self.proof_fileupload    = FileUpload(required = False, max_values = 10)

        self.add_item(self.reason_input)

        if self.length_input is not None:
            self.add_item(self.length_input)

        self.add_item(
            Label(
                text        = "DM",
                description = "Whether to DM the user.",
                component   = self.dm_checkbox,
            ),
        )

        if self.appealable_checkbox is not None:
            self.add_item(
                Label(
                    text        = "Appealable",
                    description = "Whether the action is appealable. *DM must be set to true for the action to be appealable!",
                    component   = self.appealable_checkbox,
                ),
            )

        if self.proof_fileupload is not None:
            self.add_item(
                Label(
                    text        = "Proof",
                    description = "Upload a file as proof.",
                    component   = self.proof_fileupload,
                ),
            )

    @override
    async def on_submit(self, interaction : Interaction) -> None:

        # ⸻ You cannot make an action appealable without DMing the user.

        if self.appealable_checkbox is not None and self.appealable_checkbox.value and not self.dm_checkbox.value:
            await format_send(
                interaction,
                msg_type = "warning",
                title    = "compile window",
                subtitle = "You cannot make an action appealable without DMing the user.",
            )
            return

        # ⸻ Improper time signature.

        length_value = self.length_input.value.strip().lower() if self.length_input is not None else ""
        if length_value and not match(r"^(\d+[hmds])+$", length_value):
            await format_send(
                interaction,
                msg_type =  "warning",
                title    =  "compile window",
                subtitle = f"The time signature `{self.length_input.value if self.length_input is not None else ''}` is not valid. Use formats like 10m, 2h, 1d.",
            )
            return

        user_id = self.target.id if self.target else 0
        if user_id == 0:
            self.editor.state_map.clear()

        entry : _StateEntry = {
            "reason"  : self.reason_input.value,
            "dm_user" : self.dm_checkbox.value,
        }

        if self.length_input is not None:
            entry["length"] = self.length_input.value

        if self.appealable_checkbox is not None:
            entry["appealable"] = self.appealable_checkbox.value

        if self.proof_fileupload is not None:
            filename      : str | None = next((f.filename for f in self.proof_fileupload.values), None)
            entry["file"] = filename

        self.editor.state_map[user_id] = entry
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
            label    = _build_member_label(member, resolved, self.action_type)

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
                entry           = _resolve_state(member, self.state_map, global_entry)
                missing : list[str] = []
                if not entry or not entry.get("reason"):
                    missing.append("reason")
                if self.action_type == "Timeout Add" and (not entry or not entry.get("length")):
                    missing.append("timer")
                if missing:
                    errors.append(f"- {member.mention}: Missing {format_values(missing)}")

            if errors:
                try:
                    await format_send(
                        interaction,
                        msg_type = "warning",
                        title    = "moderate members",
                        subtitle = (
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
                        reason  = escape_markdown(entry.get("reason", "N/A"))
                        dm_user = "Yes" if entry.get("dm_user") else "No"

                        lines : list[str] = [
                            f"{member.mention}",
                            f"`      Reason:` {reason}",
                        ]

                        if _wants_length(self.action_type):
                            lines.append(f"`      Length:` {entry.get('length', 'N/A')}")

                        lines.append(f"`     DM Sent:` {dm_user}")

                        if _wants_extra(self.action_type):
                            appealable = "Yes" if entry.get("appealable") else "No"
                            file       = escape_markdown(entry.get("file") or "None")
                            lines.extend(
                                [
                                    f"`  Appealable:` {appealable}",
                                    f"`  Attachment:` {file}",
                                ],
                            )

                        summary_lines.append("\n".join(lines))
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
class ModerationTargetView(View):
    type_map : MappingProxyType[ActionType, str] = MappingProxyType(
        {
            "Ban Add"           : "Select members to ban...",
            "Ban Remove"        : "Select members to un-ban...",
            "Kick"              : "Select members to kick...",
            "Quarantine Add"    : "Select members to place in quarantine...",
            "Quarantine Remove" : "Select members to remove from quarantine...",
            "Timeout Add"       : "Select members to place in timeout...",
            "Timeout Remove"    : "Select members to remove from timeout...",
        },
    )

    def __init__(self, action_type : ActionType) -> None:
        super().__init__(timeout = None)
        self.action_type : ActionType = action_type

        select = cast(UserSelect[Self], self.slct_moderation_members)
        select.placeholder = self.type_map[action_type]

    @select(cls = UserSelect, max_values = 1)
    async def slct_moderation_members(
        self,
        interaction : Interaction,
        select      : UserSelect[Self],
    ) -> None:
        chosen_members = select.values
        guild          = interaction.guild

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
            mentions      = [m.mention for m in other_members]

            word_user = "user" if len(mentions) == 1 else "users"
            word_is   = "is"   if len(mentions) == 1 else "are"

            await send_bad_argument(
                interaction,
                subtitle = {None : f"The {word_user} {format_values(mentions)} {word_is} higher in the hierarchy than you; {guild.me.mention} is unmoderatable."},
                footer   = "Bad argument. Use the native discord /kick or /ban command to remove me from the guild...",
            )
            return

        # ⸻ You cannot moderate yourself.

        if interaction.user in chosen_members:
            await send_bad_argument(
                interaction,
                subtitle = {None : "You cannot moderate yourself."},
            )
            return

        # ⸻ You cannot moderate those higher in the hierarchy than you.

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

        # ⸻ Success!

        members = [user for user in select.values if isinstance(user, Member)]

        try:
            await interaction.response.edit_message(view = _EditorView(self.action_type, members = members))

        # ⸻ Unhandled error.

        except Exception:
            await send_bad_operation(interaction, title = "compile window")
            raise
