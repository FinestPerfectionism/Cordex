from dataclasses import dataclass
from typing import Literal, cast, final

from discord import Color, Embed, TextChannel, Thread

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
    "lockdown_add",
    "lockdown_remove",
    "ban_add",
    "ban_remove",
    "kick",
    "quarantine_add",
    "quarantine_remove",
    "timeout_add",
    "timeout_remove",
    "purge",
    "note_add",
    "note_edit",
    "note_remove",
]

CASE_MAP : dict[case_types, CaseData] = {
    "lockdown_add"      : CaseType.LOCKDOWN_ADD,
    "lockdown_remove"   : CaseType.LOCKDOWN_REMOVE,
    "ban_add"           : CaseType.BAN_ADD,
    "ban_remove"        : CaseType.BAN_REMOVE,
    "kick"              : CaseType.KICK,
    "quarantine_add"    : CaseType.QUARANTINE_ADD,
    "quarantine_remove" : CaseType.QUARANTINE_REMOVE,
    "timeout_add"       : CaseType.TIMEOUT_ADD,
    "timeout_remove"    : CaseType.TIMEOUT_REMOVE,
    "purge"             : CaseType.PURGE,
    "note_add"          : CaseType.NOTE_ADD,
    "note_edit"         : CaseType.NOTE_EDIT,
    "note_remove"       : CaseType.NOTE_REMOVE,
}

async def create_case(bot : Cordex, case_type : case_types):
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
