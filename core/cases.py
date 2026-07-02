from enum import Enum
from typing import TYPE_CHECKING, Self, Literal
from discord import Color, Embed, Member
from discord.utils import utcnow

from constants import COLOR_BLACK, COLOR_BLURPLE, COLOR_GREEN, COLOR_GREY, COLOR_ORANGE, COLOR_RED, COLOR_YELLOW

class CaseType(str, Enum):
    if TYPE_CHECKING:
        case_color : Color
        case_title : str

    LOCKDOWN_ADD      = ("lockdown_add",    COLOR_GREY,  "Lockdown Added")
    LOCKDOWN_REMOVE   = ("lockdown_remove", COLOR_GREEN, "Lockdown Removed")

    BAN_ADD           = ("ban_add",    COLOR_BLACK, "Member Ban Added")
    BAN_REMOVE        = ("ban_remove", COLOR_GREEN, "Member Ban Removed")

    KICK              = ("kick", COLOR_RED, "Member Kicked")

    QUARANTINE_ADD    = ("quarantine_add",    COLOR_ORANGE, "Member Quarantine Added")
    QUARANTINE_REMOVE = ("quarantine_remove", COLOR_GREEN,  "Member Quarantine Removed")

    TIMEOUT_ADD       = ("timeout_add",    COLOR_YELLOW, "Member Timeout Added")
    TIMEOUT_REMOVE    = ("timeout_remove", COLOR_GREEN,  "Member Timeout Removed")

    PURGE             = ("purge", COLOR_BLURPLE, "Messages Purged")

    NOTE_ADD          = ("note_add",    COLOR_BLURPLE, "Note Added")
    NOTE_EDIT         = ("note_edit",   COLOR_BLURPLE, "Note Edited")
    NOTE_REMOVE       = ("note_remove", COLOR_BLURPLE, "Note Removed")

    def __new__(cls, value : str, color : Color, title : str) -> Self:
        obj = str.__new__(cls, value)
        obj._value_ = value

        obj.case_color = color
        obj.case_title = title
        return obj

CaseTypeString = Literal[
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
    "note_remove"
]

async def moderation_log(
    action_type : CaseType | CaseTypeString,
    moderator   : Member   | str,
    targets     : list[Member],
) -> None:
    embed = Embed(title = f"Case ... — {CaseType(action_type).case_title}", timestamp = utcnow())
    embed.add_field(
        name  = "Mdderator",
        value = (
            f"{moderator.mention}\n"
            f"`{moderator.name}`\n"
            f"`{moderator.id}`"
        ) if isinstance(moderator, Member) else moderator
    )
    
    if len(targets) == 1:
        target = targets[0]
        embed.add_field(
            name  =  "Target",
            value = (
                f"{target.mention}\n"
                f"`{target.name}`\n"
                f"`{target.id}`"
            )
        )
    else:
        embed.add_field(
            name  = "Targets",
            value = "\n".join(target.mention for target in targets),
        )
