import asyncio
from builtins import exec
from collections.abc import Awaitable, Callable
from contextlib import redirect_stdout
from io import StringIO
from textwrap import indent
from traceback import format_exc
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt, get, utcnow

import constants
from bot import Context, ContextOrInteraction, Cordex, Interaction, tree, ui
from bot.ui import (
    BaseContainer,
    BaseLayoutView,
    ButtonSection,
    Container,
    HiddenLargeSeparator,
    HiddenSmallSeparator,
    LayoutView,
    ThumbnailSection,
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
from core.exceptions import send_bad_argument, send_bad_permissions_command
from core.paginator import UnnamedPaginator
from core.paginator.named import NamedPaginator
from core.responses import format_message, format_send
from core.utilities import (
    codeblock,
    format_command,
    format_table,
    format_values,
    truncate,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

eval_message_ids : dict[int, int] = {}

async def run_bo_eval(bot : Cordex, ctx : Context, body : str) -> None:
    env : dict[str, object] = {
        "bot"  : bot,
        "ctx"  : ctx,
        "tree" : tree,

        "channel" : ctx.channel,
        "author"  : ctx.author,
        "guild"   : ctx.guild,
        "message" : ctx.message,

        "Context"              : Context,
        "Interaction"          : Interaction,
        "ContextOrInteraction" : ContextOrInteraction,

        "constants"    : constants,
        "asyncio"      : asyncio,
        "commands"     : commands,
        "app_commands" : app_commands,
        "discord"      : discord,
        "ui"           : ui,

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

        "utcnow"         : utcnow,
        "get"            : get,
        "codeblock"      : codeblock,
        "truncate"       : truncate,
        "format_dt"      : format_dt,
        "format_command" : format_command,
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

        "View"           : ui.View,
        "LayoutView"     : LayoutView,
        "BaseLayoutView" : BaseLayoutView,
        "Modal"          : ui.Modal,

        "Container"     : Container,
        "BaseContainer" : BaseContainer,
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

        "NamedPaginator"   : NamedPaginator,
        "UnnamedPaginator" : UnnamedPaginator,
    }

    # ⸻ I would put significantly more thought into a check for this but Cordex doesn't use enough prefix commands to really warrant it.

    if ctx.author.id != BOT_OWNER_ID:
        await send_bad_permissions_command(ctx)
        return

    if not body:
        await send_bad_argument(ctx, subtitle = {"body" : "This is a required argument was ommitted."})

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
