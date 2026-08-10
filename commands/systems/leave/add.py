from datetime import UTC, datetime, timedelta
from re import sub
from typing import Self, final, override

from dateparser import parse
from discord import Member

from bot import Interaction, log
from bot.ui import (
    ActionRow,
    Button,
    Label,
    LayoutView,
    Modal,
    TextDisplay,
    TextInput,
    button,
    grey,
    red,
)
from constants import CONTESTED_EMOJI, STAFF_ROLES
from core.exceptions import send_bad_argument, send_bad_operation
from core.permissions import is_director, is_staff

from ._base import STAFF_NAME_PATTERN, WarningView

_WORD_NUMBERS : dict[str, str] = {
    "a"     : "1",
    "an"    : "1",
    "one"   : "1",
    "two"   : "2",
    "three" : "3",
    "four"  : "4",
    "five"  : "5",
    "six"   : "6",
    "seven" : "7",
    "eight" : "8",
    "nine"  : "9",
    "ten"   : "10",
}

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /leave add Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _ChoiceRow(ActionRow["_HardCleanView"]):
    def __init__(self, target : Member) -> None:
        super().__init__()
        self.target = target

    @button(label = "Yes", style = red)
    async def btn_yes(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        target = self.target

        if not self.view:
            return

        for child in self.walk_children():
            if isinstance(child, Button):
                child.disabled = True

        roles_to_remove = [role for role in target.roles if role.id in STAFF_ROLES]

        try:
            await target.remove_roles(*roles_to_remove)
        except Exception:
            log.exception("Failed to remove hard clean %s", target.name)
            await send_bad_operation(
                interaction,
                title    = f"hard clean {target.mention}",
                subtitle = f"An exception occurred while removing {target.mention}'s staff roles. Aborting.",
            )
        else:
            self.view.text   = "Hard clean successful."
            self.view.footer = f"Removed {len(roles_to_remove)} roles from {target.mention}"
        finally:
            await interaction.response.edit_message(view = self.view)

    @button(label = "No", style = grey)
    async def btn_no(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        if not self.view:
            return

        for child in self.walk_children():
            if isinstance(child, Button):
                child.disabled = True

        self.view.text   = "Hard clean aborted."
        self.view.footer = "No action was taken."

        await interaction.response.edit_message(view = self.view)

@final
class _HardCleanView(WarningView):
    def __init__(self, target : Member) -> None:
        super().__init__(
            subtitle = f"You are about to hard clean {target.mention}. This action is intended for demotion and will require manual intervention to restore. Proceed?",
            footer   =  "This action is __not reversable__",
            row      = _ChoiceRow(target),
        )

@final
class _LeaveModal(Modal, title = "Leave"):
    def __init__(self, target : Member | None = None) -> None:
        super().__init__()
        name = f"{target.name}'s" if target else "your"

        self.start_dt : datetime | None = None
        self.end_dt   : datetime | None = None

        self._timer = TextInput[Self](
            placeholder = 'ex: "30m, 2d"',
            default     = "1 Day",
            required    = False,
        )
        self.timer  = Label[Self](
            text        =  "Timer",
            description = f"Set a duration for {name} leave.",
            component   = self._timer,
        )

        self._start_date = TextInput[Self](
            placeholder = 'ex: "Tomorrow at 3pm, in 2 days"',
            required    = False,
        )
        self.start_date  = Label[Self](
            text        =  "Start Date",
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
        self.add_items(
            TextDisplay[Self](f"{CONTESTED_EMOJI} **Use `Timer` alone, `Start Date` + `Timer`, or `Start Date` + `End Date`.**"),
            self.timer,
            self.start_date,
            self.end_date,
        )

    # ⸻ Parsing methods.

    @staticmethod
    def _normalize_text(value : str) -> str:
        text  = sub(r"\band\b", "", value.lower().strip())
        words = text.split()
        return " ".join(_WORD_NUMBERS.get(word, word) for word in words)

    @classmethod
    def _parse_timer(cls, value : str) -> timedelta | None:
        cleaned = cls._normalize_text(value)
        now     = datetime.now(UTC)
        expr    = cleaned if cleaned.startswith("in ") else f"in {cleaned}"

        parsed = parse(
            expr,
            settings = {
                "RELATIVE_BASE"            : now,
                "PREFER_DATES_FROM"        : "future",
                "RETURN_AS_TIMEZONE_AWARE" : True,
            },
        )
        if parsed is None or parsed <= now:
            return None

        return parsed - now

    @classmethod
    def _parse_datetime(cls, value : str) -> datetime | None:
        cleaned = cls._normalize_text(value)
        now     = datetime.now(UTC)

        if cleaned == "now":
            return now

        return parse(
            cleaned,
            settings = {
                "RELATIVE_BASE"            : now,
                "PREFER_DATES_FROM"        : "future",
                "RETURN_AS_TIMEZONE_AWARE" : True,
            },
        )

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        timer = bool(self._timer.value)
        start = bool(self._start_date.value)
        end   = bool(self._end_date.value)

        # ⸻ At least one field is required.

        if not (timer or start or end):
            await send_bad_argument(
                interaction,
                subtitle = {None : "At least 1 argument must be chosen."},
            )
            return

        # ⸻ All three fields cannot be provided together.

        if timer and start and end:
            await send_bad_argument(
                interaction,
                subtitle = {("Timer", "Start Date", "End Date") : "Cannot specify all three fields. Use either `Start Date` + `End Date`, or `Start Date` + `Timer`, or `Timer`)."},
            )
            return

        # ⸻ End Date and Timer are incompatible.

        if end and timer:
            await send_bad_argument(
                interaction,
                subtitle = {("Timer", "End Date") : "`Timer` is incompatible with `End Date`."},
            )
            return

        # ⸻ End Date requires Start Date.

        if end and not start:
            await send_bad_argument(
                interaction,
                subtitle = {"End Date" : "`End Date` is dependent on `Start Date`."},
            )
            return

        # ⸻ Start Date requires Timer or End Date.

        if start and not (timer or end):
            await send_bad_argument(
                interaction,
                subtitle = {"Start Date" : "`Start Date` is dependent on either `Timer` or `End Date`."},
            )
            return

        # ⸻ Parse and validate Start Date.

        now      = datetime.now(UTC)
        start_dt = now

        if start:
            parsed_start = self._parse_datetime(self._start_date.value)
            if parsed_start is None:
                await send_bad_argument(
                    interaction,
                    subtitle = {"Start Date" : "Invalid start date. (ex: 'now', 'tomorrow', 'in 3 minutes')"},
                )
                return
            start_dt = parsed_start

        # ⸻ Parse and validate Timer or End Date.

        if timer:
            duration = self._parse_timer(self._timer.value)
            if duration is None:
                await send_bad_argument(
                    interaction,
                    subtitle = {"Timer" : "Invalid timer format. (ex: '3 days', '3d', 'three days 5m')"},
                )
                return
            self.start_dt = start_dt
            self.end_dt   = start_dt + duration

        elif end:
            parsed_end = self._parse_datetime(self._end_date.value)
            if parsed_end is None:
                await send_bad_argument(
                    interaction,
                    subtitle = {"End Date" : "Invalid end date. (ex: 'tomorrow', 'in an hour', 'in a week')"},
                )
                return

            if parsed_end <= start_dt:
                await send_bad_argument(
                    interaction,
                    subtitle = {"End Date" : "`End Date` must be strictly after `Start Date`."},
                )
                return

            self.start_dt = start_dt
            self.end_dt   = parsed_end

def _validate_staff_name(target : Member) -> bool:
    return bool(STAFF_NAME_PATTERN.match(target.display_name))

async def _validate_target(interaction : Interaction, target : Member) -> bool:
    is_self = (target.id == interaction.user.id)

    if is_director(target) and not is_self:
        await send_bad_argument(
            interaction,
            subtitle = {"target" : "You cannot vacate other directors."},
        )
        return False

    if not is_staff(target):
        error = "You are not staff." if is_self else "You cannot vacate those who are not staff."

        await send_bad_argument(
            interaction,
            subtitle = {"target" : error},
        )
        return False

    if not _validate_staff_name(target):
        error = "You do not have a valid staff name format." if is_self else f"{target.mention} does not have a valid staff name format."

        await send_bad_argument(
            interaction,
            subtitle = {"target" : error},
        )
        return False

    return True

async def run_leave_add(
    interaction : Interaction,
    target      : Member | None = None,
    leave_type  : str    | None = None,
) -> None:

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not isinstance(interaction.user, Member):
        return

    effective_target = target or interaction.user
    is_self          = (effective_target.id == interaction.user.id)

    if not await _validate_target(interaction, effective_target):
        return

    match leave_type:
        case "standard" | "soft_clean" | None:
            await interaction.response.send_modal(_LeaveModal(None if is_self else effective_target))
            return
        case "hard_clean":
            if is_self:
                await send_bad_argument(
                    interaction,
                    subtitle = {"target" : "You cannot hard clean yourself."},
                )
                return

            await interaction.response.send_message(view = _HardCleanView(effective_target), ephemeral = True)
        case _:
            pass
