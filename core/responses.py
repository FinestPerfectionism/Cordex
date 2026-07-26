from typing import TYPE_CHECKING, Literal, cast

from discord import AllowedMentions, Interaction, Message
from discord.abc import Messageable

from constants import (
    ACCEPTED_EMOJI,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    FORUM_EMOJI,
    LOCKED_FORUM_EMOJI,
    STANDSTILL_EMOJI,
)

if TYPE_CHECKING:
    from bot import ContextOrInteraction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Response Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type _MessageType = Literal["success", "warning", "error", "information", "lock", "unlock"]
type _SendTarget = "ContextOrInteraction | Messageable"

def _emoji_match(msg_type : _MessageType) -> str:
    match msg_type:
        case "success":
            return ACCEPTED_EMOJI
        case "information":
            return STANDSTILL_EMOJI
        case "warning":
            return CONTESTED_EMOJI
        case "error":
            return DENIED_EMOJI
        case "lock":
            return LOCKED_FORUM_EMOJI
        case "unlock":
            return FORUM_EMOJI

def _title_match(msg_type : _MessageType) -> str:
    match msg_type:
        case "success":
            return "Successfully"
        case "information" | "lock" | "unlock":
            return ""
        case "warning" | "error":
            return "Failed to"

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Internal Builders
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def _build_title(msg_type : _MessageType, title : str, *, override : bool = False) -> str:
    if override:
        return f"{_emoji_match(msg_type)} **{title}**"

    prefix      = _title_match(msg_type)
    punctuation = "!" if msg_type in {"warning", "error"} else "."
    clean_title = title.rstrip(".!") + punctuation

    if prefix:
        return f"{_emoji_match(msg_type)} **{prefix} {clean_title}**"
    return f"{_emoji_match(msg_type)} **{clean_title}**"

def build_footer(footer : str | None) -> str | None:
    if footer is None:
        return None
    return f"{footer.rstrip('. ')}."

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Internal Send
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def _send(
    target       : _SendTarget,
    /,
    *,
    content      : str,
    ephemeral    : bool                   = True,
    delete_after : float           | None = None,
    message      : Message         | None = None,
    mentions     : AllowedMentions | None = None,
) -> Message | None:
    if isinstance(target, Interaction):
        if target.response.is_done():
            return await target.followup.send(
                content          = content,
                ephemeral        = ephemeral,
                allowed_mentions = mentions or AllowedMentions.all(),
            )

        await target.response.send_message(
            content          = content,
            ephemeral        = ephemeral,
            allowed_mentions = mentions or AllowedMentions.all(),
        )
        return await target.original_response()

    if message is not None:
        return await message.edit(
            content          = content,
            delete_after     = delete_after,
            allowed_mentions = mentions or AllowedMentions.all(),
        )

    if delete_after is not None:
        return await cast(Messageable, target).send(
            content          = content,
            delete_after     = delete_after,
            allowed_mentions = mentions or AllowedMentions.all(),
        )

    return await cast(Messageable, target).send(
        content          = content,
        allowed_mentions = mentions or AllowedMentions.all(),
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Custom Message Builders
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_message(
    *,
    msg_type : _MessageType,
    title    : str,
    subtitle : str | None = None,
    footer   : str | None = None,
    override : bool       = False,
) -> str:
    lines : list[str] = [_build_title(msg_type, title, override = override)]

    if subtitle:
        lines.append(subtitle)

    footer_text = build_footer(footer)
    if footer_text:
        lines.append(f"-# {footer_text}")

    return "\n".join(lines)

async def format_send(
    target       : _SendTarget,
    /,
    *,
    msg_type     : _MessageType,
    title        : str,
    subtitle     : str             | None = None,
    footer       : str             | None = None,
    override     : bool                   = False,
    ephemeral    : bool                   = True,
    delete_after : float           | None = None,
    message      : Message         | None = None,
    mentions     : AllowedMentions | None = None,
) -> Message | None:
    content = format_message(
        msg_type = msg_type,
        title    = title,
        subtitle = subtitle,
        footer   = footer,
        override = override,
    )
    return await _send(
        target,
        content      = content,
        ephemeral    = ephemeral,
        delete_after = delete_after,
        message      = message,
        mentions     = mentions,
    )
