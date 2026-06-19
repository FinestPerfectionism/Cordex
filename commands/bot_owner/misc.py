import contextlib
import io
import textwrap
import traceback
from builtins import exec
from typing import TYPE_CHECKING, cast

import discord
from discord import ui
from discord.ext import commands

from bot import Context, Cordex, Interaction, tree
from core.exceptions import send_bad_operation
from core.utilities import (
    HiddenLargeSeparator,
    HiddenSmallSeparator,
    VisibleLargeSeparator,
    VisibleSmallSeparator,
    codeblock,
    format_values,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

from constants import (
    ACCEPTED_EMOJI,
    COLOR_BLACK,
    COLOR_BLURPLE,
    COLOR_GREEN,
    COLOR_GREY,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_YELLOW,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    STANDSTILL_EMOJI,
)
from core.responses import (
    edit_custom_message,
    format_custom_message,
    multi_custom_message,
    send_custom_message,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_misc_sync(ctx : Context) -> None:
    try:
        _ = await tree.sync()
        _ = await send_custom_message(
            ctx,
            msg_type = "success",
            title    = "synced app command tree",
            subtitle = "Successfully globally synced the app command tree.",
        )

    except discord.DiscordException as e:
        await send_bad_operation(
            ctx,
            title    = "sync app command tree",
            subtitle = codeblock(f"{e}"),
        )
        return

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


eval_message_ids : dict[int, int] = {}

async def run_bo_misc_eval(bot : Cordex, ctx : Context, body : str) -> None:
    env : dict[str, object] = {
        "bot"                   : bot,
        "ctx"                   : ctx,
        "tree"                  : tree,
        "channel"               : ctx.channel,
        "author"                : ctx.author,
        "guild"                 : ctx.guild,
        "message"               : ctx.message,

        "commands"              : commands,
        "Context"               : Context,
        "Interaction"           : Interaction,

        "ACCEPTED_EMOJI"        : ACCEPTED_EMOJI,
        "CONTESTED_EMOJI"       : CONTESTED_EMOJI,
        "DENIED_EMOJI"          : DENIED_EMOJI,
        "STANDSTILL_EMOJI"      : STANDSTILL_EMOJI,

        "COLOR_BLURPLE"         : COLOR_BLURPLE,
        "COLOR_GREEN"           : COLOR_GREEN,
        "COLOR_YELLOW"          : COLOR_YELLOW,
        "COLOR_ORANGE"          : COLOR_ORANGE,
        "COLOR_RED"             : COLOR_RED,
        "COLOR_GREY"            : COLOR_GREY,
        "COLOR_BLACK"           : COLOR_BLACK,

        "discord"               : discord,
        "ui"                    : ui,

        "codeblock"             : codeblock,
        "format_values"         : format_values,
        "format_custom_message" : format_custom_message,
        "send_custom_message"   : send_custom_message,
        "edit_custom_message"   : edit_custom_message,
        "multi_custom_message"  : multi_custom_message,

        "select"                : ui.select,
        "button"                : ui.button,

        "Button"                : ui.Button,
        "Select"                : ui.Select,
        "UserSelect"            : ui.UserSelect,
        "RoleSelect"            : ui.RoleSelect,
        "MentionableSelect"     : ui.MentionableSelect,
        "ChannelSelect"         : ui.ChannelSelect,
        "TextInput"             : ui.TextInput,

        "View"                  : ui.View,
        "LayoutView"            : ui.LayoutView,
        "Modal"                 : ui.Modal,

        "Container"             : ui.Container,
        "Section"               : ui.Section,
        "Separator"             : ui.Separator,
        "ActionRow"             : ui.ActionRow,
        "TextDisplay"           : ui.TextDisplay,
        "Thumbnail"             : ui.Thumbnail,
        "MediaGallery"          : ui.MediaGallery,
        "File"                  : ui.File,
        "FileUpload"            : ui.FileUpload,
        "Label"                 : ui.Label,

        "VLSep"                 : VisibleLargeSeparator,
        "VSSep"                 : VisibleSmallSeparator,
        "HLSep"                 : HiddenLargeSeparator,
        "HSSep"                 : HiddenSmallSeparator,

        "RadioGroup"            : ui.RadioGroup,
        "Checkbox"              : ui.Checkbox,
        "CheckboxGroup"         : ui.CheckboxGroup,

        "SeparatorSpacing"      : discord.SeparatorSpacing,
        "MediaGalleryItem"      : discord.MediaGalleryItem,
        "SelectOption"          : discord.SelectOption,
        "ButtonStyle"           : discord.ButtonStyle,
        "TextStyle"             : discord.TextStyle,
        "RadioGroupOption"      : discord.RadioGroupOption,
        "CheckboxGroupOption"   : discord.CheckboxGroupOption,
        "SelectDefaultValue"    : discord.SelectDefaultValue,

        "Embed"                 : discord.Embed,
        "Poll"                  : discord.Poll,

        "Item"                  : ui.Item,
        "DynamicItem"           : ui.DynamicItem,
    }

    body       = "\n".join(body.split("\n")[1:-1]) if body.startswith("```") else body.strip("` \n")
    stdout     = io.StringIO()
    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
    try:
        exec(to_compile, env)
    except Exception as e:
        _ = await ctx.message.add_reaction(f"{DENIED_EMOJI}")
        res = await ctx.send(codeblock(f"{e.__class__.__name__}: {e}"))
        eval_message_ids[ctx.message.id] = res.id
        return
    func = cast("Callable[[], Awaitable[object]]", env["func"])
    try:
        with contextlib.redirect_stdout(stdout):
            ret = await func()
    except Exception:
        value = stdout.getvalue()
        _ = await ctx.message.add_reaction(f"{CONTESTED_EMOJI}")
        res   = await ctx.send(codeblock(f"{value}{traceback.format_exc()}"))
        eval_message_ids[ctx.message.id] = res.id
    else:
        value = stdout.getvalue()
        _ = await ctx.message.add_reaction(f"{ACCEPTED_EMOJI}")

        if ret is None:
            if value:
                res = await ctx.send(codeblock(value))
                eval_message_ids[ctx.message.id] = res.id
        else:
            res = await ctx.send(codeblock(f"{value}{ret}"))
            eval_message_ids[ctx.message.id] = res.id
