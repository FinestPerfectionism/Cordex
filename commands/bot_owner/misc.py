import asyncio
import contextlib
import io
import textwrap
import traceback
from typing import TYPE_CHECKING, cast

import discord
from discord import ui
from discord.ext import commands

from bot import Context, Interaction, tree
from core.exceptions import send_bad_argument, send_bad_operation, send_unknown_error
from core.utilities import (
    HiddenLargeSeparator,
    HiddenSmallSeparator,
    VisibleLargeSeparator,
    VisibleSmallSeparator,
    format_values,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bot import Cordex

from constants import (
    ACCEPTED_EMOJI,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    STANDSTILL_EMOJI,
    COLOR_BLURPLE,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_GREY,
    COLOR_BLACK,
)
from core.responses import multi_custom_message, send_custom_message
from events.messages.on_edit import MessageEditHandler

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
            subtitle = (
                "```py\n"
               f"{e}\n"
                "```"
            ),
        )
        return

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_misc_eval(bot : "Cordex", ctx : Context, body : str) -> None:
    env : dict[str, object] = {
        "bot"                  : bot,
        "ctx"                  : ctx,
        "tree"                 : tree,
        "channel"              : ctx.channel,
        "author"               : ctx.author,
        "guild"                : ctx.guild,
        "message"              : ctx.message,

        "commands"             : commands,
        "Context"              : Context,
        "Interaction"          : Interaction,

        "ACCEPTED_EMOJI"       : ACCEPTED_EMOJI,
        "CONTESTED_EMOJI"      : CONTESTED_EMOJI,
        "DENIED_EMOJI"         : DENIED_EMOJI,
        "STANDSTILL_EMOJI"     : STANDSTILL_EMOJI,

        "COLOR_BLURPLE"        : COLOR_BLURPLE,
        "COLOR_GREEN"          : COLOR_GREEN,
        "COLOR_YELLOW"         : COLOR_YELLOW,
        "COLOR_ORANGE"         : COLOR_ORANGE,
        "COLOR_RED"            : COLOR_RED,
        "COLOR_GREY"           : COLOR_GREY,
        "COLOR_BLACK"          : COLOR_BLACK,

        "discord"              : discord,
        "ui"                   : ui,

        "format_values"        : format_values,
        "send_custom_message"  : send_custom_message,
        "multi_custom_message" : multi_custom_message,

        "select"               : ui.select,
        "button"               : ui.button,

        "Button"               : ui.Button,
        "Select"               : ui.Select,
        "UserSelect"           : ui.UserSelect,
        "RoleSelect"           : ui.RoleSelect,
        "MentionableSelect"    : ui.MentionableSelect,
        "ChannelSelect"        : ui.ChannelSelect,
        "TextInput"            : ui.TextInput,

        "View"                 : ui.View,
        "LayoutView"           : ui.LayoutView,
        "Modal"                : ui.Modal,

        "Container"            : ui.Container,
        "Section"              : ui.Section,
        "Separator"            : ui.Separator,
        "ActionRow"            : ui.ActionRow,
        "TextDisplay"          : ui.TextDisplay,
        "Thumbnail"            : ui.Thumbnail,
        "MediaGallery"         : ui.MediaGallery,
        "File"                 : ui.File,
        "FileUpload"           : ui.FileUpload,
        "Label"                : ui.Label,

        "VLSep"                : VisibleLargeSeparator,
        "VSSep"                : VisibleSmallSeparator,
        "HLSep"                : HiddenLargeSeparator,
        "HSSep"                : HiddenSmallSeparator,

        "RadioGroup"           : ui.RadioGroup,
        "Checkbox"             : ui.Checkbox,
        "CheckboxGroup"        : ui.CheckboxGroup,

        "SeparatorSpacing"     : discord.SeparatorSpacing,
        "MediaGalleryItem"     : discord.MediaGalleryItem,
        "SelectOption"         : discord.SelectOption,
        "ButtonStyle"          : discord.ButtonStyle,
        "TextStyle"            : discord.TextStyle,
        "RadioGroupOption"     : discord.RadioGroupOption,
        "CheckboxGroupOption"  : discord.CheckboxGroupOption,
        "SelectDefaultValue"   : discord.SelectDefaultValue,

        "Embed"                : discord.Embed,
        "Poll"                 : discord.Poll,

        "Item"                 : ui.Item,
        "DynamicItem"          : ui.DynamicItem,
    }

    body       = "\n".join(body.split("\n")[1:-1]) if body.startswith("```") else body.strip("` \n")
    stdout     = io.StringIO()
    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
    try:
        import builtins
        builtins.exec(to_compile, env)
    except Exception as e:
        _ = await ctx.message.add_reaction(f"{DENIED_EMOJI}")
        _ = await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")
        return
    func = cast("Callable[[], Awaitable[object]]", env["func"])
    try:
        with contextlib.redirect_stdout(stdout):
            ret = await func()
    except Exception:
        value = stdout.getvalue()
        _ = await ctx.message.add_reaction(f"{CONTESTED_EMOJI}")
        _ = await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
    else:
        value = stdout.getvalue()
        _ = await ctx.message.add_reaction(f"{ACCEPTED_EMOJI}")

        resp = None
        if ret is None:
            if value:
                resp = await ctx.send(f"```py\n{value}\n```")
        else:
            resp = await ctx.send(f"```py\n{value}{ret}\n```")

        handler = bot.get_cog("MessageEditHandler")
        if resp and isinstance(handler, MessageEditHandler):
            handler.eval_responses[ctx.message.id] = resp.id

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner say Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_misc_say(
    interaction : Interaction,
    channel     : discord.abc.Messageable,
    text        : str,
    message_id  : str | None = None,
) -> None:
    _ = await interaction.response.defer(ephemeral = True)

    typing_speed = len(text) * 0.05
    typing_delay = min(typing_speed, 10.0)

    try:
        reply_reference : discord.Message | None = None

        if message_id:
            try:
                if channel:
                    reply_reference = await channel.fetch_message(int(message_id))
            except (discord.NotFound, ValueError, discord.HTTPException):
                await send_bad_argument(interaction, subtitle = {"message-id" : "The message provided does not exist, I lack permissions to access it, or it is not a valid ID."})
                return

        if hasattr(channel, "typing"):
            async with channel.typing():
                await asyncio.sleep(typing_delay)

        if reply_reference:
            _ = await reply_reference.reply(content = text)
        else:
            _ = await channel.send(content = text)

        await interaction.followup.send("Sent!", ephemeral = True)

    except discord.Forbidden:
        _ = await send_unknown_error(interaction)
        return
