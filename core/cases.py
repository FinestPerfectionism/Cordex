from dataclasses import dataclass
from typing import Literal, cast, final

from discord import Color, Embed, Member, TextChannel, Thread

from bot import Cordex
from constants import (
    COLOR_BLACK,
    COLOR_BLURPLE,
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
    moderator  : Member
    target     : Member
    reason     : str
    dm_user    : bool
    appealable : bool

@dataclass
class BanAddPayload(BaseAddPayload):
    length : int | None


type BanRemovePayload = BaseRemovePayload

@dataclass
class KickPayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool

@dataclass
class TimeoutAddPayload(BaseAddPayload):
    length : int


type TimeoutRemovePayload = BaseRemovePayload

@dataclass
class QuarantineAddPayload(BaseAddPayload):
    length : int | None


type QuarantineRemovePayload = BaseRemovePayload

@dataclass
class PurgePayload:
    moderator : Member
    target    : Member
    reason    : str

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# ...
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@dataclass(frozen = True)
class CaseData:
    value      : str
    case_color : Color
    case_title : str

@final
class CaseType:
    LOCKDOWN_ADD      = CaseData("lockdown_add",    COLOR_GREY,  "Lockdown Added")
    LOCKDOWN_REMOVE   = CaseData("lockdown_remove", COLOR_GREEN, "Lockdown Removed")

    BAN_ADD           = CaseData("ban_add",    COLOR_BLACK, "Member Ban Added")
    BAN_REMOVE        = CaseData("ban_remove", COLOR_GREEN, "Member Ban Removed")

    KICK              = CaseData("kick", COLOR_RED, "Member Kicked")

    QUARANTINE_ADD    = CaseData("quarantine_add",    COLOR_ORANGE, "Member Quarantine Added")
    QUARANTINE_REMOVE = CaseData("quarantine_remove", COLOR_GREEN,  "Member Quarantine Removed")

    TIMEOUT_ADD       = CaseData("timeout_add",    COLOR_YELLOW, "Member Timeout Added")
    TIMEOUT_REMOVE    = CaseData("timeout_remove", COLOR_GREEN,  "Member Timeout Removed")

    PURGE             = CaseData("purge", COLOR_BLURPLE, "Messages Purged")

    NOTE_ADD          = CaseData("note_add",    COLOR_BLURPLE, "Note Added")
    NOTE_EDIT         = CaseData("note_edit",   COLOR_BLURPLE, "Note Edited")
    NOTE_REMOVE       = CaseData("note_remove", COLOR_BLURPLE, "Note Removed")


case_types = Literal[
    "Lockdown Add",
    "Lockdown Remove",
    "Ban Add",
    "Ban Remove",
    "Kick",
    "Quarantine Add",
    "Quarantine Remove",
    "Timeout Add",
    "Timeout Remove",
    "Purge",
    "Note Add",
    "Note Edit",
    "Note Remove",
]

CASE_MAP : dict[case_types, CaseData] = {
    "Lockdown Add"      : CaseType.LOCKDOWN_ADD,
    "Lockdown Remove"   : CaseType.LOCKDOWN_REMOVE,
    "Ban Add"           : CaseType.BAN_ADD,
    "Ban Remove"        : CaseType.BAN_REMOVE,
    "Kick"              : CaseType.KICK,
    "Quarantine Add"    : CaseType.QUARANTINE_ADD,
    "Quarantine Remove" : CaseType.QUARANTINE_REMOVE,
    "Timeout Add"       : CaseType.TIMEOUT_ADD,
    "Timeout Remove"    : CaseType.TIMEOUT_REMOVE,
    "Purge"             : CaseType.PURGE,
    "Note Add"          : CaseType.NOTE_ADD,
    "Note Edit"         : CaseType.NOTE_EDIT,
    "Note Remove"       : CaseType.NOTE_REMOVE,
}

async def create_case(bot : Cordex, case_type : case_types) -> None:
    cursor = await bot.db.execute(
        """
        SELECT config_value FROM GuildConfig
        WHERE config_key = 'logging_moderation_channel'
        """,
    )
    row = await cursor.fetchone()

    channel_id = row[0] if row else None

    if channel_id is None:
        return

    validated_id = cast(int, channel_id)
    channel = await bot.fetch_channel(validated_id)

    if not isinstance(channel, TextChannel | Thread):
        return

    data  = CASE_MAP[case_type]
    embed = Embed(title = data.case_title, color = data.case_color)

    await channel.send(embed = embed)
