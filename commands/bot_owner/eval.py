import asyncio
from builtins import exec
from collections.abc import Awaitable, Callable
from contextlib import redirect_stdout
from io import StringIO
from textwrap import indent
from traceback import format_exc
from typing import cast

import discord
from discord import ui
from discord.ext import commands
from discord.utils import format_dt, get, utcnow

from bot import Context, Cordex, Interaction, tree
from bot.ui import (
    ButtonSection,
    ChannelModalSelect,
    Container,
    HiddenLargeSeparator,
    HiddenSmallSeparator,
    MentionableModalSelect,
    ModalSelect,
    RoleModalSelect,
    ThumbnailSection,
    UserModalSelect,
    VisibleLargeSeparator,
    VisibleSmallSeparator,
)
from constants import (
    ACCEPTED_EMOJI,
    BOT_OWNER_ID,
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_BLURPLE,
    COLOR_GREEN,
    COLOR_GREY,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_YELLOW,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    STANDSTILL_EMOJI,
)
from core.exceptions import send_bad_permissions_command
from core.responses import format_message, format_send
from core.utilities import codeblock, format_table, format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

eval_message_ids : dict[int, int] = {}

async def run_bo_eval(bot : Cordex, ctx : Context, body : str) -> None:
    env : dict[str, object] = {
        "bot"     : bot,
        "ctx"     : ctx,
        "tree"    : tree,
        "channel" : ctx.channel,
        "author"  : ctx.author,
        "guild"   : ctx.guild,
        "message" : ctx.message,

        "commands"    : commands,
        "Context"     : Context,
        "Interaction" : Interaction,

        "ACCEPTED_EMOJI"   : ACCEPTED_EMOJI,
        "CONTESTED_EMOJI"  : CONTESTED_EMOJI,
        "DENIED_EMOJI"     : DENIED_EMOJI,
        "STANDSTILL_EMOJI" : STANDSTILL_EMOJI,

        "COLOR_BLURPLE" : COLOR_BLURPLE,
        "COLOR_BLUE"    : COLOR_BLUE,
        "COLOR_GREEN"   : COLOR_GREEN,
        "COLOR_YELLOW"  : COLOR_YELLOW,
        "COLOR_ORANGE"  : COLOR_ORANGE,
        "COLOR_RED"     : COLOR_RED,
        "COLOR_GREY"    : COLOR_GREY,
        "COLOR_BLACK"   : COLOR_BLACK,
        "COLOR_WHITE"   : COLOR_WHITE,

        "asyncio" : asyncio,
        "discord" : discord,
        "ui"      : ui,

        "utcnow"         : utcnow,
        "get"            : get,
        "codeblock"      : codeblock,
        "format_dt"      : format_dt,
        "format_values"  : format_values,
        "format_message" : format_message,
        "format_send"    : format_send,
        "format_table"   : format_table,

        "select" : ui.select,
        "button" : ui.button,

        "Button"            : ui.Button,
        "Select"            : ui.Select,
        "UserSelect"        : ui.UserSelect,
        "RoleSelect"        : ui.RoleSelect,
        "MentionableSelect" : ui.MentionableSelect,
        "ChannelSelect"     : ui.ChannelSelect,
        "TextInput"         : ui.TextInput,

        "View"       : ui.View,
        "LayoutView" : ui.LayoutView,
        "Modal"      : ui.Modal,

        "Container"     : Container,
        "BaseContainer" : ui.Container,
        "Section"       : ui.Section,
        "Separator"     : ui.Separator,
        "ActionRow"     : ui.ActionRow,
        "TextDisplay"   : ui.TextDisplay,
        "Thumbnail"     : ui.Thumbnail,
        "MediaGallery"  : ui.MediaGallery,
        "File"          : ui.File,
        "FileUpload"    : ui.FileUpload,
        "Label"         : ui.Label,

        "ButtonSection"    : ButtonSection,
        "ThumbnailSection" : ThumbnailSection,
        "BSec"             : ButtonSection,
        "TSec"             : ThumbnailSection,

        "VisibleLargeSeparator" : VisibleLargeSeparator,
        "VisibleSmallSeparator" : VisibleSmallSeparator,
        "HiddenLargeSeparator"  : HiddenLargeSeparator,
        "HiddenSmallSeparator"  : HiddenSmallSeparator,
        "VLSep"                 : VisibleLargeSeparator,
        "VSSep"                 : VisibleSmallSeparator,
        "HLSep"                 : HiddenLargeSeparator,
        "HSSep"                 : HiddenSmallSeparator,

        "ModalSelect"            : ModalSelect,
        "UserModalSelect"        : UserModalSelect,
        "RoleModalSelect"        : RoleModalSelect,
        "MentionableModalSelect" : MentionableModalSelect,
        "ChannelModalSelect"     : ChannelModalSelect,
        "MSelect"                : ModalSelect,
        "UMSelect"               : UserModalSelect,
        "RMSelect"               : RoleModalSelect,
        "MMSelect"               : MentionableModalSelect,
        "CMSelect"               : ChannelModalSelect,

        "RadioGroup"    : ui.RadioGroup,
        "Checkbox"      : ui.Checkbox,
        "CheckboxGroup" : ui.CheckboxGroup,

        "SeparatorSpacing"    : discord.SeparatorSpacing,
        "MediaGalleryItem"    : discord.MediaGalleryItem,
        "SelectOption"        : discord.SelectOption,
        "ButtonStyle"         : discord.ButtonStyle,
        "TextStyle"           : discord.TextStyle,
        "RadioGroupOption"    : discord.RadioGroupOption,
        "CheckboxGroupOption" : discord.CheckboxGroupOption,
        "SelectDefaultValue"  : discord.SelectDefaultValue,

        "Embed" : discord.Embed,
        "Poll"  : discord.Poll,

        "AllowedMentions" : discord.AllowedMentions,
    }

    # ⸻ I would put significantly more thought into a check for this but Cordex doesn't use enough prefix commands to really warrant it.

    if ctx.author.id != BOT_OWNER_ID:
        await send_bad_permissions_command(ctx)
        return

    message = ctx.message

    body       = "\n".join(body.split("\n")[1:-1]) if body.startswith("```") else body.strip("` \n")
    stdout     = StringIO()
    to_compile = (
        f"async def func():\n"
        f"{indent(body, "  ")}"
    )

    try:
        exec(to_compile, env)
    except Exception as e:
        await message.add_reaction(DENIED_EMOJI)
        res = await ctx.send(codeblock(f"{e.__class__.__name__}: {e}"))
        eval_message_ids[message.id] = res.id
        return

    func = cast(Callable[[], Awaitable[object]], env["func"])

    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception:
        value = stdout.getvalue()
        await message.add_reaction(CONTESTED_EMOJI)
        res   = await ctx.send(codeblock(f"{value}{format_exc()}"))

        eval_message_ids[message.id] = res.id
    else:
        value = stdout.getvalue()
        await message.add_reaction(ACCEPTED_EMOJI)

        if ret is None:
            if value:
                res = await ctx.send(codeblock(value))
                eval_message_ids[message.id] = res.id
        else:
            res = await ctx.send(codeblock(f"{value}{ret}"))
            eval_message_ids[message.id] = res.id
