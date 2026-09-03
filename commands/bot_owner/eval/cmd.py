import asyncio
from collections.abc import Awaitable, Callable
from contextlib import redirect_stdout
from io import StringIO
from textwrap import indent
from traceback import format_exc
from typing import cast

import discord
from discord import Message, app_commands
from discord.ext import commands
from discord.utils import format_dt, get, utcnow

import constants
from bot import Context, ContextOrInteraction, Interaction, bot, log, ui
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
from core.paginator import NamedPaginator, PageData, UnnamedPaginator
from core.permissions import is_bot_owner
from core.responses import format_message, format_send
from core.utilities import (
    codeblock,
    format_command,
    format_now,
    format_table,
    format_values,
    truncate,
)

from .tools import format_dict, show_attrs, show_def

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

eval_message_ids : dict[int, int] = {}

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Command Edit Listener
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@bot.listen("on_message_edit")
async def message_edit_handler(_before : Message, after : Message) -> None:
    target_id = int(after.id)

    # ⸻ Eval command editing.

    log.info(f"Pre-eval log block. Target ID: {target_id}, Map: {eval_message_ids}")
    if target_id in eval_message_ids:
        log.info("Entered primary eval block.")

        # ⸻ Remove our old reactions.

        if bot.user is not None:
            log.info("Entered 'self.bot.user is not None' block.")
            for reaction in after.reactions:
                log.info("Entered 'for reaction in reactions' block.")
                if reaction.me:
                    log.info("Entered 'if reaction.me' block.")
                    try:
                        await reaction.remove(bot.user)
                    except Exception:
                        log.exception("Failure in eval command reinvocation — 'reaction.remove(self.bot.user)'")

        # ⸻ Remove our old response.

        old_response_id = eval_message_ids.pop(target_id, None)
        if old_response_id is not None:
            log.info("Entered 'if old_response_id is not None' block.")

            try:
                old_msg = await after.channel.fetch_message(int(old_response_id))
                await old_msg.delete()
            except Exception:
                log.exception("Failure in eval command reinvocation — 'old_msg.delete()'")

        # ⸻ Reinvoke the command.

        try:
            ctx = await bot.get_context(after)
            await bot.invoke(ctx)
        except Exception:
            log.exception("Failure in eval command reinvocation — 'self.bot.invoke(ctx)'")

        return

async def run_bo_eval(ctx : Context, body : str) -> None:
    env : dict[str, object] = {
        "bot"  : ctx.bot,
        "ctx"  : ctx,
        "tree" : ctx.bot.tree,

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
        "show_def"       : show_def,
        "show_attrs"     : show_attrs,
        "format_dt"      : format_dt,
        "format_now"     : format_now,
        "format_command" : format_command,
        "format_values"  : format_values,
        "format_message" : format_message,
        "format_send"    : format_send,
        "format_table"   : format_table,
        "format_dict"    : format_dict,

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
        "PageData"         : PageData,
    }

    # ⸻ I would put significantly more thought into a check for this but Cordex doesn't use enough prefix commands to warrant it.

    if not is_bot_owner(ctx.author):
        await ctx.send(
            format_message(
                msg_type = "warning",
                title    = "run command",
                subtitle = "This command can only be run in a guild",
                footer   = "Bad environment",
            ),
        )
        return

    if not body:
        await ctx.send(
            format_message(
                msg_type = "error",
                title    = "",
                subtitle = "`body`: This is a required argument was ommitted.",
                footer   = "Bad argumnt",
            ),
        )
        return

    message = ctx.message

    body       = "\n".join(body.split("\n")[1 : -1]) if body.startswith("```") else body.strip("` \n")
    stdout     = StringIO()
    to_compile = (
        f"async def func():\n"
        f"{indent(body, "  ")}"
    )

    try:
        exec(to_compile, env)  # ruff: ignore[exec-builtin]
    except Exception as e:
        await message.add_reaction(DENIED_EMOJI)
        res = await ctx.send(codeblock(f"{e.__class__.__name__}: {e}"))
        eval_message_ids[int(message.id)] = int(res.id)
        return

    func = cast("Callable[[], Awaitable[object]]", env["func"])

    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception:
        value = stdout.getvalue()
        await message.add_reaction(CONTESTED_EMOJI)
        res   = await ctx.send(codeblock(f"{value}{format_exc()}"))

        eval_message_ids[int(message.id)] = int(res.id)
    else:
        value = stdout.getvalue()
        await message.add_reaction(ACCEPTED_EMOJI)

        if ret is None:
            if value:
                res = await ctx.send(codeblock(value))
                eval_message_ids[int(message.id)] = int(res.id)
        else:
            res = await ctx.send(codeblock(f"{value}{ret}"))
            eval_message_ids[int(message.id)] = int(res.id)
