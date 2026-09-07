from dataclasses import dataclass
from typing import Self, final

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


BanRemovePayload = BaseRemovePayload

@dataclass
class KickPayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool

@dataclass
class TimeoutAddPayload(BaseAddPayload):
    length : int


TimeoutRemovePayload = BaseRemovePayload

QuarantineAddPayload    = BaseAddPayload
QuarantineRemovePayload = BaseRemovePayload

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
    content : str


NoteAddPayload  = BaseNotePayload
NoteEditPayload = BaseNotePayload

@dataclass
class NoteRemovePayload:
    target : Member


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
# Actions Class
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

        @final
        class CaseView(LayoutView):
            container = Container[Self](
                TextDisplay(f"# {data.title}"),
                VisibleLargeSeparator(),
                color = data.color,
            )

        await log_channel.send(
            view             = CaseView(),
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
