from __future__ import annotations

from itertools import starmap
from typing import (
    Literal,
    cast,
    overload,
)

from discord import Interaction, Message
from discord.abc import Messageable
from discord.ui import LayoutView, TextDisplay

from bot import CtxOrInteraction
from constants import (
    ACCEPTED_EMOJI,
    BOT_OWNER_ID,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    STANDSTILL_EMOJI,
)
from core.utilities import VisibleSmallSeparator

type TextDisplayOrSeparator = list[TextDisplay[LayoutView] | VisibleSmallSeparator]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Response Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

MessageType    = Literal[
    "success",
    "warning",
    "error",
    "information",
]
SubMessageType = Literal[
    "warning",
    "error",
]

SendTarget = CtxOrInteraction | Messageable

class _Subfield:
    def __init__(
        self,
        *,
        subtitle          : str | None,
        footer            : str | None,
        contact_bot_owner : bool,
    ) -> None:
        self.subtitle          : str | None = subtitle
        self.footer            : str | None = footer
        self.contact_bot_owner : bool       = contact_bot_owner

class _Field:
    def __init__(
        self,
        *,
        title     : str,
        msg_type  : SubMessageType,
        subfields : list[_Subfield],
        override  : bool = False,
    ) -> None:
        self.title     : str             = title
        self.msg_type  : SubMessageType  = msg_type
        self.subfields : list[_Subfield] = subfields
        self.override  : bool            = override

def emoji(msg_type : MessageType | SubMessageType) -> str:
    match msg_type:
        case "success":
            return f"{ACCEPTED_EMOJI}"
        case "information":
            return f"{STANDSTILL_EMOJI}"
        case "warning":
            return f"{CONTESTED_EMOJI}"
        case "error":
            return f"{DENIED_EMOJI}"

def type_prefix(msg_type : MessageType | SubMessageType) -> str:
    match msg_type:
        case "success":
            return "Successfully"
        case "information":
            return ""
        case "warning":
            return "Failed to"
        case "error":
            return "Failed to"

def build_header(msg_type : MessageType | SubMessageType, title : str, *, override : bool = False) -> str:
    if override:
        return f"{emoji(msg_type)} **{title}**"

    prefix      = type_prefix(msg_type)
    punctuation = "!" if msg_type in {"warning", "error"} else "."
    clean_title = title.rstrip(".!") + punctuation

    if prefix:
        return f"{emoji(msg_type)} **{prefix} {clean_title}**"
    return f"{emoji(msg_type)} **{clean_title}**"

def build_footer_text(footer : str | None, *, contact_bot_owner : bool) -> str | None:
    if footer is None and not contact_bot_owner:
        return None

    base = footer or ""

    if contact_bot_owner:
        if base:
            return f"{base.rstrip('. ')}. Contact <@{BOT_OWNER_ID}>."
        return f"Contact <@{BOT_OWNER_ID}>."
    return f"{base.rstrip('. ')}."

def build_view(content : str) -> LayoutView:
    class _SingleView(LayoutView):
        text : TextDisplay[_SingleView] = TextDisplay(content = content)

    return _SingleView()

def build_multi_view(all_components : TextDisplayOrSeparator) -> LayoutView:
    class _MultiView(LayoutView):
        pass

    view = _MultiView()
    for component in all_components:
        _ = view.add_item(component)
    return view

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
            return await target.followup.send(
                view      = view,
                ephemeral = ephemeral,
            )
        _ = await target.response.send_message(
            view      = view,
            ephemeral = ephemeral,
        )
        return None

    if message is not None:
        return await message.edit(view = view)

    if delete_after is not None:
        return await cast("Messageable", target).send(
            view         = view,
            delete_after = delete_after,
        )

    return await cast("Messageable", target).send(view = view)

async def edit(message : Message, view : LayoutView) -> Message:
    return await message.edit(view = view)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# send_custom_message Response
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@overload
async def send_custom_message(
    target       : SendTarget,
    *,
    msg_type     : Literal["success", "information"],
    title        : str,
    subtitle     : str     | None = ...,
    footer       : str     | None = ...,
    override     : bool           = ...,
    ephemeral    : bool           = ...,
    delete_after : float   | None = ...,
    message      : Message | None = ...,
) -> Message | None:
    ...

@overload
async def send_custom_message(
    target            : SendTarget,
    *,
    msg_type          : Literal["warning", "error"],
    title             : str,
    subtitle          : str     | None = ...,
    footer            : str     | None = ...,
    contact_bot_owner : bool           = ...,
    override          : bool           = ...,
    ephemeral         : bool           = ...,
    delete_after      : float   | None = ...,
    message           : Message | None = ...,
) -> Message | None:
    ...

async def send_custom_message(
    target            : SendTarget,
    *,
    msg_type          : MessageType,
    title             : str,
    subtitle          : str     | None = None,
    footer            : str     | None = None,
    contact_bot_owner : bool           = False,
    override          : bool           = False,
    ephemeral         : bool           = True,
    delete_after      : float   | None = None,
    message           : Message | None = None,
) -> Message | None:
    allow_contact = contact_bot_owner if msg_type in {"warning", "error"} else False

    lines : list[str] = [
        build_header(
            msg_type,
            title,
            override = override,
        ),
    ]
    if subtitle:
        lines.append(subtitle)
    footer_text = build_footer_text(
        footer,
        contact_bot_owner = allow_contact,
    )
    if footer_text:
        lines.append(f"-# {footer_text}")

    content = "\n".join(lines)

    return await send(
        target,
        build_view(content),
        ephemeral    = ephemeral,
        delete_after = delete_after,
        message      = message,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# edit_custom_message Response
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@overload
async def edit_custom_message(
    message  : Message,
    *,
    msg_type : Literal["success", "information"],
    title    : str,
    subtitle : str | None = ...,
    footer   : str | None = ...,
    override : bool       = ...,
) -> Message:
    ...

@overload
async def edit_custom_message(
    message           : Message,
    *,
    msg_type          : Literal["warning", "error"],
    title             : str,
    subtitle          : str | None = ...,
    footer            : str | None = ...,
    contact_bot_owner : bool       = ...,
    override          : bool       = ...,
) -> Message:
    ...

async def edit_custom_message(
    message           : Message,
    *,
    msg_type          : MessageType,
    title             : str,
    subtitle          : str | None = None,
    footer            : str | None = None,
    contact_bot_owner : bool       = False,
    override          : bool       = False,
) -> Message:
    allow_contact = contact_bot_owner if msg_type in {"warning", "error"} else False

    lines : list[str] = [
        build_header(
            msg_type,
            title,
            override = override,
        ),
    ]
    if subtitle:
        lines.append(subtitle)
    footer_text = build_footer_text(
        footer,
        contact_bot_owner = allow_contact,
    )
    if footer_text:
        lines.append(f"-# {footer_text}")

    content = "\n".join(lines)

    return await edit(message, build_view(content))

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# multi_custom_message Response
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class _MultiCustomMessage:
    def __init__(self, target : SendTarget) -> None:
        self._target       : SendTarget     = target
        self._fields       : list[_Field]   = []
        self._ephemeral    : bool           = True
        self._delete_after : float   | None = None
        self._message      : Message | None = None

    def set_ephemeral(self, *, value : bool = True) -> _MultiCustomMessage:
        self._ephemeral = value
        return self

    def set_delete_after(self, *, value : float | None) -> _MultiCustomMessage:
        self._delete_after = value
        return self

    def set_message(self, *, message : Message) -> _MultiCustomMessage:
        self._message = message
        return self

    @staticmethod
    def add_subfield(
        *,
        subtitle          : str | None = None,
        footer            : str | None = None,
        contact_bot_owner : bool       = False,
    ) -> _Subfield:
        return _Subfield(
            subtitle          = subtitle,
            footer            = footer,
            contact_bot_owner = contact_bot_owner,
        )

    def add_field(
        self,
        *,
        title     : str,
        msg_type  : SubMessageType,
        subfields : list[_Subfield],
        override  : bool = False,
    ) -> _MultiCustomMessage:
        self._fields.append(
            _Field(
                title     = title,
                msg_type  = msg_type,
                subfields = subfields,
                override  = override,
            ),
        )
        return self

    def render_field_blocks(self, field : _Field) -> list[str]:
        def build_block(index : int, subfield : _Subfield) -> str:
            lines : list[str] = []

            if index == 0:
                lines.append(
                    build_header(
                        cast("MessageType", field.msg_type),
                        field.title,
                        override = field.override,
                    ),
                )

            if subfield.subtitle:
                lines.append(subfield.subtitle)

            footer_text = build_footer_text(
                subfield.footer,
                contact_bot_owner = subfield.contact_bot_owner,
            )
            if footer_text:
                lines.append(f"-# {footer_text}")

            return "\n".join(lines)

        return list(starmap(build_block, enumerate(field.subfields)))

    def build_components(self) -> TextDisplayOrSeparator:
        all_components : TextDisplayOrSeparator = []

        for field_index, field in enumerate(self._fields):
            if field_index > 0:
                all_components.append(VisibleSmallSeparator())
            all_components.extend(
                TextDisplay(content = block)
                for block in self.render_field_blocks(field)
            )

        return all_components

    def has_errors(self) -> bool:
        return len(self._fields) > 0

    async def send(self) -> Message | None:
        if not self.has_errors():
            return None

        return await send(
            self._target,
            build_multi_view(self.build_components()),
            ephemeral    = self._ephemeral,
            delete_after = self._delete_after,
            message      = self._message,
        )

    async def edit(self, message : Message) -> Message | None:
        if not self.has_errors():
            return None

        return await edit(
            message,
            build_multi_view(self.build_components()),
        )

def multi_custom_message(target : SendTarget) -> _MultiCustomMessage:
    return _MultiCustomMessage(target)

@overload
def format_custom_message(
    *,
    msg_type : Literal["success", "information"],
    title    : str,
    subtitle : str | None = ...,
    footer   : str | None = ...,
    override : bool       = ...,
) -> str:
    ...

@overload
def format_custom_message(
    *,
    msg_type          : Literal["warning", "error"],
    title             : str,
    subtitle          : str | None = ...,
    footer            : str | None = ...,
    contact_bot_owner : bool       = ...,
    override          : bool       = ...,
) -> str:
    ...

def format_custom_message(
    *,
    msg_type          : MessageType,
    title             : str,
    subtitle          : str | None = None,
    footer            : str | None = None,
    contact_bot_owner : bool       = False,
    override          : bool       = False,
) -> str:
    allow_contact = contact_bot_owner if msg_type in {"warning", "error"} else False

    lines : list[str] = [
        build_header(
            msg_type,
            title,
            override = override,
        ),
    ]
    if subtitle:
        lines.append(subtitle)
    footer_text = build_footer_text(
        footer,
        contact_bot_owner = allow_contact,
    )
    if footer_text:
        lines.append(f"-# {footer_text}")

    return "\n".join(lines)
