from typing import Literal, Self, cast

from discord import Interaction, Message
from discord.abc import Messageable
from discord.ui import LayoutView, TextDisplay

from bot import ContextOrInteraction
from constants import (
    ACCEPTED_EMOJI,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    STANDSTILL_EMOJI,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Response Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

MessageType = Literal["success", "warning", "error", "information"]
SendTarget = ContextOrInteraction | Messageable

def emoji(msg_type : MessageType) -> str:
    match msg_type:
        case "success":
            return ACCEPTED_EMOJI
        case "information":
            return STANDSTILL_EMOJI
        case "warning":
            return CONTESTED_EMOJI
        case "error":
            return DENIED_EMOJI

def type_prefix(msg_type : MessageType) -> str:
    match msg_type:
        case "success":
            return "Successfully"
        case "information":
            return ""
        case "warning" | "error":
            return "Failed to"

def build_header(msg_type : MessageType, title : str, *, override : bool = False) -> str:
    if override:
        return f"{emoji(msg_type)} **{title}**"

    prefix      = type_prefix(msg_type)
    punctuation = "!" if msg_type in {"warning", "error"} else "."
    clean_title = title.rstrip(".!") + punctuation

    if prefix:
        return f"{emoji(msg_type)} **{prefix} {clean_title}**"
    return f"{emoji(msg_type)} **{clean_title}**"

def build_footer_text(footer : str | None) -> str | None:
    if footer is None:
        return None
    return f"{footer.rstrip('. ')}."

def build_view(content : str) -> LayoutView:
    class SingleView(LayoutView):
        text : TextDisplay[Self] = TextDisplay(content = content)
    return SingleView()

async def send(
    target       : SendTarget,
    view         : LayoutView,
    *,
    ephemeral    : bool           = True,
    delete_after : float   | None = None,
    message      : Message | None = None,
) -> Message | None:
    if isinstance(target, Interaction):
        if target.response.is_done():
            return await target.followup.send(view = view, ephemeral = ephemeral)
        await target.response.send_message(view = view, ephemeral = ephemeral)
        return None

    if message is not None:
        return await message.edit(view = view)

    if delete_after is not None:
        return await cast(Messageable, target).send(view = view, delete_after = delete_after)

    return await cast(Messageable, target).send(view = view)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Custom Message Builders
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_build(
    *,
    msg_type : MessageType,
    title    : str,
    subtitle : str | None = None,
    footer   : str | None = None,
    override : bool       = False,
) -> str:
    lines : list[str] = [build_header(msg_type, title, override = override)]
    if subtitle:
        lines.append(subtitle)

    footer_text = build_footer_text(footer)
    if footer_text:
        lines.append(f"-# {footer_text}")

    return "\n".join(lines)

async def format_send(
    target       : SendTarget,
    /,
    *,
    msg_type     : MessageType,
    title        : str,
    subtitle     : str     | None = None,
    footer       : str     | None = None,
    override     : bool           = False,
    ephemeral    : bool           = True,
    delete_after : float   | None = None,
    message      : Message | None = None,
) -> Message | None:
    content = format_build(
        msg_type = msg_type,
        title    = title,
        subtitle = subtitle,
        footer   = footer,
        override = override,
    )
    return await send(
        target,
        build_view(content),
        ephemeral    = ephemeral,
        delete_after = delete_after,
        message      = message,
    )
