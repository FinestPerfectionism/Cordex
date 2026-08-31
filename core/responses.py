from typing import Literal, Self, final

from discord import AllowedMentions, Interaction, Message
from discord.abc import Messageable

from bot import ContextOrInteraction
from constants import (
    ACCEPTED_EMOJI,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    FORUM_EMOJI,
    LOCKED_FORUM_EMOJI,
    STANDSTILL_EMOJI,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Response Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type _MessageType = Literal["success", "warning", "error", "information", "lock", "unlock"]
type _SendTarget = ContextOrInteraction | Messageable

@final
class PunctuationOverride:
    def __init__(
        self,
        *,
        title    : bool | None = None,
        subtitle : bool | None = None,
        footer   : bool | None = None,
    ) -> None:
        super().__init__()
        self.title    = title
        self.subtitle = subtitle
        self.footer   = footer

    @classmethod
    def all_true(cls) -> Self:
        return cls(title = True, subtitle = True, footer = True)

    @classmethod
    def all_false(cls) -> Self:
        return cls(title = False, subtitle = False, footer = False)

@final
class ResponseOverride:
    def __init__(
        self,
        *,
        prefix      : bool                       = True,
        punctuation : PunctuationOverride | None = None,
    ) -> None:
        super().__init__()
        self.prefix      = prefix
        self.punctuation = punctuation or PunctuationOverride()

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

def _apply_punctuation(text : str, default : str, *, setting : bool | None) -> str:
    if setting is False:
        return text

    if setting is True:
        return text + default

    if text.endswith((".", "?", "!", ",")):
        return text

    return text + default

def _build_title(msg_type : _MessageType, title : str, config : ResponseOverride) -> str:
    prefix         = _title_match(msg_type) if config.prefix else ""
    default_punc   = "!" if msg_type in {"warning", "error"} else "."
    clean_title    = _apply_punctuation(title, default_punc, setting = config.punctuation.title)

    if prefix:
        return f"{_emoji_match(msg_type)} **{prefix} {clean_title}**"
    return f"{_emoji_match(msg_type)} **{clean_title}**"

def _build_subtitle(subtitle : str | None, config : ResponseOverride) -> str | None:
    if subtitle is None:
        return None
    return _apply_punctuation(subtitle, ".", setting = config.punctuation.subtitle)

def _build_footer(footer : str | None, config : ResponseOverride) -> str | None:
    if footer is None:
        return None
    return _apply_punctuation(footer, ".", setting = config.punctuation.footer)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Internal Send
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def _send(
    target       : _SendTarget,
    /,
    *,
    content      : str,
    ephemeral    : bool                   = True,
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
            allowed_mentions = mentions or AllowedMentions.all(),
        )

    return await target.send(
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
    subtitle : str              | None = None,
    footer   : str              | None = None,
    override : ResponseOverride | None = None,
) -> str:
    config = override or ResponseOverride()
    lines : list[str] = [_build_title(msg_type, title, config)]

    subtitle_text = _build_subtitle(subtitle, config)
    if subtitle_text:
        lines.append(subtitle_text)

    footer_text = _build_footer(footer, config)
    if footer_text:
        lines.append(f"-# {footer_text}")

    return "\n".join(lines)

async def format_send(
    target       : _SendTarget,
    /,
    *,
    msg_type     : _MessageType,
    title        : str,
    subtitle     : str              | None = None,
    footer       : str              | None = None,
    ephemeral    : bool                    = True,
    message      : Message          | None = None,
    mentions     : AllowedMentions  | None = None,
    override     : ResponseOverride | None = None,
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
        message      = message,
        mentions     = mentions,
    )
