from typing import Self, final, override

from discord import Member

from bot import Interaction
from bot.ui import (
    ActionRow,
    Button,
    Label,
    LayoutView,
    Modal,
    TextInput,
    button,
    grey,
    red,
)
from core.exceptions import send_bad_argument
from core.permissions import is_director

from ._base import WarningView

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /leave add Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _ChoiceRow(ActionRow[LayoutView]):
    def __init__(self) -> None:
        super().__init__()

    @button(label = "Yes", style = red)
    async def btn_yes(self, _interaction : Interaction, _button : Button[LayoutView]) -> None:
        ...

    @button(label = "No", style = grey)
    async def btn_no(self, _interaction : Interaction, _button : Button[LayoutView]) -> None:
        ...

@final
class _HardCleanView(WarningView):
    def __init__(self, target : Member) -> None:
        super().__init__(
            subtitle = f"You are about to hard clean {target.mention}. This action is intended for demotion and will require manual intervention to restore. Proceed?",
            footer   =  "This action is __not reversable__!",
            row      = _ChoiceRow(),
        )

@final
class _LeaveModal(Modal, title = "Leave"):
    def __init__(self, target : Member | None = None) -> None:
        super().__init__()
        name = f"{target.name}'s" if target else "your"

        self._timer = TextInput[Self](
            placeholder = 'ex: "30m, 2d"',
            default     = "1 Day",
            required    = False,
        )
        self.timer  = Label[Self](
            text        = "Timer",
            description = "Set a timer for leave.",
            component   = self._timer,
        )

        self._start_date = TextInput[Self](
            placeholder = 'ex: "Tomorrow at 3pm, in 2 days"',
            required    = False,
        )
        self.start_date  = Label[Self](
            text        =  "Start Date (Requires 'End Date')",
            description = f"Set a start date for {name} leave.",
            component   = self._start_date,
        )

        self._end_date = TextInput[Self](
            placeholder = 'ex: "Tomorrow at 3pm, in 2 days"',
            required    = False,
        )
        self.end_date  = Label[Self](
            text        =  "End Date (Requires 'Start Date')",
            description = f"Set an end date for {name} leave.",
            component   = self._end_date,
        )
        self.add_items(self.timer, self.start_date, self.end_date)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        ...

async def run_leave_add(
    interaction : Interaction,
    target      : Member | None = None,
    leave_type  : str    | None = None,
) -> None:

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not isinstance(interaction.user, Member):
        return

    match leave_type:
        case "none":
            await interaction.response.send_modal(_LeaveModal(target or interaction.user))
        case "soft_clean" | None:
            await interaction.response.send_modal(_LeaveModal(target or interaction.user))
        case "hard_clean":
            if not target or target.id == interaction.user.id:
                await send_bad_argument(
                    interaction,
                    subtitle = {("target", "leave-type") : "You cannot hard clean yourself."},
                )

            elif target and is_director(target):
                await send_bad_argument(
                    interaction,
                    subtitle = {("target", "leave-type") : "You cannot hard clean a director."},
                )

            elif target:
                await interaction.response.send_message(view = _HardCleanView(target), ephemeral = True)
        case _:
            pass
