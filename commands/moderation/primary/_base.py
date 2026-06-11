import re
from collections.abc import Sequence

from discord import (
    AllowedMentions,
    ButtonStyle,
    Emoji,
    Member,
    PartialEmoji,
)
from discord.ui import (
    ActionRow,
    Button,
    Checkbox,
    Container,
    FileUpload,
    Label,
    LayoutView,
    Modal,
    Section,
    TextDisplay,
    TextInput,
    UserSelect,
    View,
    select,
)
from typing_extensions import override

from bot import Interaction
from constants import ACCEPTED_EMOJI
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import send_custom_message
from core.utilities import (
    VisibleLargeSeparator,
    blurple,
    check_role_hierarchy,
    format_values,
    green,
    grey,
    red,
)

type StateEntry = dict[str, str | bool | None]
type StateMap   = dict[int, StateEntry]

def build_member_label(member : Member, state : StateEntry | None) -> str:
    if not state:
        return member.mention

    lines = [member.mention, f"**Reason:** \"{state['r']}\""]
    lines.append(f"**Timer:** `{state['t']}`")
    lines.append(f"**Appealable:** `{state.get('a', False)}`")
    lines.append(f"**DM:** `{state.get('d', False)}`")

    if "f" in state:
        lines.append(f"**File:** `{state['f']}`")

    return "\n".join(lines)

def resolve_state(
    member       : Member,
    state_map    : StateMap,
    global_state : StateEntry | None,
) -> StateEntry | None:
    return state_map.get(member.id) or global_state

class ActionButton(Button[LayoutView]):
    def __init__(
        self,
        target    : Member                     | None,
        editor    : "EditorView",
        *,
        style     : ButtonStyle                       = grey,
        label     : str                        | None = None,
        disabled  : bool                              = False,
        custom_id : str                        | None = None,
        url       : str                        | None = None,
        emoji     : str | Emoji | PartialEmoji | None = None,
        row       : int                        | None = None,
        sku_id    : int                        | None = None,
    ) -> None:
        super().__init__(
            style     = style,
            label     = label,
            disabled  = disabled,
            custom_id = custom_id,
            url       = url,
            emoji     = emoji,
            row       = row,
            sku_id    = sku_id,
        )
        self.target : Member | None = target
        self.editor : "EditorView"  = editor

    @override
    async def callback(self, interaction : Interaction) -> None:
        try:
            _ = await interaction.response.send_modal(ReasonModal(self.target, self.editor))
        except Exception:
            await send_bad_operation(interaction, title = "open modal")
            raise

class ReasonModal(Modal):
    def __init__(self, target : Member | None, editor : "EditorView") -> None:
        title = f"Reason: {target.name}" if target else "Global Action"
        super().__init__(title = title)
        self.target : Member | None = target
        self.editor : "EditorView"  = editor

        existing : StateEntry = editor.state_map.get(
            target.id if target else 0,
            editor.state_map.get(0, {}),
        )

        self.reason_input : TextInput[Modal] = TextInput[Modal](
            label       = "Reason",
            placeholder = 'ex: "nsfw spam"',
            default     = str(existing.get("r", "")),
            required    = True,
        )
        self.timer_input  : TextInput[Modal] = TextInput[Modal](
            label       = "Timer",
            placeholder = 'ex: "30m, 2d"',
            default     = str(existing.get("t", "")),
            required    = True,
        )
        self.appealable_box : Checkbox[Modal]   = Checkbox(default = bool(existing.get("a", False)))
        self.dm_box         : Checkbox[Modal]   = Checkbox(default = bool(existing.get("d", False)))
        self.file_upload    : FileUpload[Modal] = FileUpload(required = False, max_values = 1)

        for item in [
            self.reason_input,
            self.timer_input,
            Label(text = "Appealable", component = self.appealable_box),
            Label(text = "DM User",    component = self.dm_box),
            Label(text = "Upload",     component = self.file_upload),
        ]:
            _ = self.add_item(item)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        timer_value = self.timer_input.value.strip().lower()
        if timer_value and not re.match(r"^(\d+[hmds])+$", timer_value):
            _ = await send_custom_message(
                interaction,
                msg_type = "warning",
                title    = "compile window",
                subtitle = f"The time signature `{self.timer_input.value}` is not valid. Use formats like 10m, 2h, 1d.",
            )
            return

        user_id = self.target.id if self.target else 0
        if user_id == 0:
            self.editor.state_map.clear()

        filename : str | None = next(
            (f.filename for f in self.file_upload.values),
            None,
        )
        self.editor.state_map[user_id] = {
            "r" : self.reason_input.value,
            "t" : self.timer_input.value,
            "a" : self.appealable_box.value,
            "d" : self.dm_box.value,
            "f" : filename,
        }
        await self.editor.refresh(interaction)

class EditorView(LayoutView):
    def __init__(self, members : Sequence[Member] | None = None) -> None:
        super().__init__(timeout = None)
        self.members   : list[Member] = list(members) if members else []
        self.state_map : StateMap     = {}
        self.rebuild()

    def rebuild(self) -> None:
        _ = self.clear_items()
        container : Container[LayoutView] = Container()
        global_state                      = self.state_map.get(0)

        for member in self.members:
            resolved = resolve_state(member, self.state_map, global_state)
            label    = build_member_label(member, resolved)

            if resolved:
                style = green if (member.id in self.state_map or 0 in self.state_map) else blurple
            else:
                style = grey

            button = ActionButton(member, self, style = style, label = "Action")
            _ = container.add_item(Section(label, accessory = button))
        _ = container.add_item(VisibleLargeSeparator())

        async def handle_execute(interaction : Interaction) -> None:
            errors : list[str] = []
            global_entry       = self.state_map.get(0)

            for member in self.members:
                entry               = resolve_state(member, self.state_map, global_entry)
                missing : list[str] = []
                if not entry or not entry.get("r"):
                    missing.append("reason")
                if not entry or not entry.get("t"):
                    missing.append("timer")
                if missing:
                    missing_string = format_values(missing)
                    errors.append(f"- {member.mention}: Missing {missing_string}")

            if errors:
                try:
                    _ = await send_custom_message(
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
                summary_lines = [f"{ACCEPTED_EMOJI} **Successfully mass moderated all members.**"]

                for member in self.members:
                    entry = resolve_state(member, self.state_map, global_entry)
                    if entry:
                        reason     = entry.get("r", "N/A")
                        timer      = entry.get("t", "N/A")
                        appealable = "Yes" if entry.get("a") else "No"
                        dm_user    = "Yes" if entry.get("d") else "No"
                        file       = entry.get("f") or "None"

                        summary_lines.append(
                            (
                                f"Success for {member.mention}.\n"
                                f"- **Reason:** {reason}\n"
                                f"- **Timer:** {timer}\n"
                                f"- **Appealable:** {appealable} **|** **DM Sent:** {dm_user}\n"
                                f"- **Attachment:** {file}"
                            )
                        )

                    else:
                        summary_lines.append(
                            (
                               f"Partial success for {member.mention}.\n"
                                "-# Missing configuration data for this member."
                            )
                        )

                class FinalizedView(LayoutView):
                    text : TextDisplay[LayoutView] = TextDisplay(content = "\n".join(summary_lines))
                _ = await interaction.response.edit_message(view = FinalizedView())

            except Exception:
                await send_bad_operation(interaction, title = "compile window")
                raise

        execute_button : Button[LayoutView] = Button(style = red, label = "Execute")
        execute_button.callback             = handle_execute

        _ = container.add_item(
            ActionRow(
                ActionButton(None, self, style = blurple, label = "Global"),
                execute_button,
            ),
        )
        _ = self.add_item(container)

    async def refresh(self, interaction : Interaction) -> None:
        self.rebuild()
        try:
            _ = await interaction.response.edit_message(
                view             = self,
                allowed_mentions = AllowedMentions.none(),
            )
        except Exception:
            await send_bad_operation(interaction, title = "compile window")
            raise

class MemberSelectView(View):
    def __init__(self) -> None:
        super().__init__(timeout = None)

    @select(cls = UserSelect, placeholder = "Choose members...", max_values = 1)
    async def member_select(
        self,
        interaction : Interaction,
        select      : UserSelect[LayoutView],
    ) -> None:
        chosen = select.values

        ineligible = [
            user.mention for user in chosen
            if isinstance(user, Member)
            and isinstance(interaction.user, Member)
            and check_role_hierarchy(interaction.user, user, ">=")
        ]

        if ineligible:
            word_user = "user" if len(ineligible) == 1 else "users"
            word_is   = "is"   if len(ineligible) == 1 else "are"

            await send_bad_argument(
                interaction,
                subtitle = {
                    "chosen" : f"The {word_user} {format_values(ineligible)} {word_is} higher in the hierarchy than you."
                }
            )
            return

        members = [user for user in select.values if isinstance(user, Member)]
        try:
            _ = await interaction.response.edit_message(view = EditorView(members = members))
        except Exception:
            await send_bad_operation(interaction, title = "compile window")
            raise
