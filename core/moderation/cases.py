from dataclasses import dataclass
from typing import final

from discord import AllowedMentions, Color, Guild, Member

from bot import Cordex
from bot.types import GuildMessagable
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_GREY,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_YELLOW,
)
from core.utilities import format_now, format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cases Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Action Payloads
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@dataclass
class BaseRemovePayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class BaseAddPayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class LockdownAddPayload:
    moderator : Member
    target    : GuildMessagable
    reason    : str


@dataclass
class LockdownRemovePayload:
    moderator : Member
    target    : GuildMessagable
    reason    : str


@dataclass
class BanAddPayload(BaseAddPayload):
    seconds_to_delete : int


@dataclass
class BanRemovePayload(BaseRemovePayload):
    pass


@dataclass
class KickPayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class TimeoutAddPayload(BaseAddPayload):
    length : int


@dataclass
class TimeoutRemovePayload(BaseRemovePayload):
    pass


@dataclass
class QuarantineAddPayload(BaseAddPayload):
    pass


@dataclass
class QuarantineRemovePayload(BaseRemovePayload):
    pass


@dataclass
class PurgePayload:
    moderator : Member
    target    : Member | None
    reason    : str
    channel   : GuildMessagable
    amount    : int
    force     : bool


@dataclass
class BaseNotePayload:
    target  : Member
    note_id : int
    content : str


@dataclass
class NoteAddPayload(BaseNotePayload):
    pass


@dataclass
class NoteEditPayload(BaseNotePayload):
    pass


@dataclass
class NoteRemovePayload:
    target  : Member
    note_id : int


Payloads = (
    LockdownAddPayload
    | LockdownRemovePayload
    | BanAddPayload
    | BanRemovePayload
    | KickPayload
    | QuarantineAddPayload
    | QuarantineRemovePayload
    | TimeoutAddPayload
    | TimeoutRemovePayload
    | PurgePayload
    | NoteAddPayload
    | NoteEditPayload
    | NoteRemovePayload
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cases Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@dataclass(frozen = True)
class CaseData:
    color : Color
    title : str


CASE_MAP : dict[type, CaseData] = {
    LockdownAddPayload      : CaseData(COLOR_GREY,   "Lockdown Added"),
    LockdownRemovePayload   : CaseData(COLOR_GREEN,  "Lockdown Removed"),
    BanAddPayload           : CaseData(COLOR_BLACK,  "Member Ban Added"),
    BanRemovePayload        : CaseData(COLOR_GREEN,  "Member Ban Removed"),
    KickPayload             : CaseData(COLOR_RED,    "Member Kicked"),
    QuarantineAddPayload    : CaseData(COLOR_ORANGE, "Member Quarantine Added"),
    QuarantineRemovePayload : CaseData(COLOR_GREEN,  "Member Quarantine Removed"),
    TimeoutAddPayload       : CaseData(COLOR_YELLOW, "Member Timeout Added"),
    TimeoutRemovePayload    : CaseData(COLOR_GREEN,  "Member Timeout Removed"),
    PurgePayload            : CaseData(COLOR_BLUE,   "Messages Purged"),
    NoteAddPayload          : CaseData(COLOR_BLUE,   "Note Added"),
    NoteEditPayload         : CaseData(COLOR_BLUE,   "Note Edited"),
    NoteRemovePayload       : CaseData(COLOR_BLUE,   "Note Removed"),
}


@final
class Cases:
    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot   = bot
        self.guild = guild

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # create_case
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def create_case(self, case : Payloads) -> None:
        log_channel = await self.bot.config(self.guild).get_moderation_logging_channel()
        if not log_channel:
            return

        data = CASE_MAP[type(case)]

        view = LayoutView()
        container = Container[view](
            TextDisplay(f"# {data.title}"),
            color = data.color,
        )

        if isinstance(case, PurgePayload):
            if case.target is not None:
                target_info = {
                    "Target"    : case.target.mention,
                    "Name"      : case.target.name,
                    "Target ID" : case.target.id,
                }

                container.add_items(
                    VisibleLargeSeparator(),
                    TextDisplay(
                        "## Target\n"
                       f"{format_table(target_info)}",
                    ),
                )
        else:
            target = case.target
            target_info = {
                "Target"    : target.mention,
                "Name"      : getattr(target, "name", str(target)),
                "Target ID" : target.id,
            }

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Target\n"
                   f"{format_table(target_info)}",
                ),
            )

        if not isinstance(case, NoteAddPayload | NoteEditPayload | NoteRemovePayload):
            moderator = case.moderator
            moderator_info = {
                "Moderator"      : moderator.mention,
                "Moderator Name" : moderator.name,
                "Moderator ID"   : moderator.id,
            }

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Moderator\n"
                   f"{format_table(moderator_info)}",
                ),
            )

        details : dict[str, object] = {}

        if isinstance(case, BanAddPayload):
            details["Message Delete History"] = f"{case.seconds_to_delete} seconds"
        elif isinstance(case, TimeoutAddPayload):
            details["Duration"] = f"{case.length} seconds"
        elif isinstance(case, PurgePayload):
            details["Channel"] = case.channel.mention
            details["Amount"]  = case.amount
            details["Forced"]  = case.force

        if isinstance(case, BaseAddPayload | BaseRemovePayload | KickPayload):
            details["DM Sent"] = case.dm_user

        if details:
            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Details\n"
                   f"{format_table(details)}",
                ),
            )

        if isinstance(
            case,
            BaseAddPayload
            | BaseRemovePayload
            | LockdownAddPayload
            | LockdownRemovePayload
            | KickPayload
            | PurgePayload,
        ) and case.reason:
            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Reason\n"
                   f"{case.reason}",
                ),
            )

        if isinstance(case, NoteAddPayload | NoteEditPayload) and case.content:
            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Content\n"
                   f"{case.content}",
                ),
            )

        container.add_items(
            VisibleLargeSeparator(),
            TextDisplay(f"-# {format_now()} | {format_now("R")}"),
        )

        view.add_item(container)

        await log_channel.send(
            view             = view,
            allowed_mentions = AllowedMentions.none(),
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_case
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_case(self) -> None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # edit_case
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def edit_case(self) -> None:
        ...
