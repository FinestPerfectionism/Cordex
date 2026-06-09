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
from core.utilities import (
    HiddenLargeSeparator,
    HiddenSmallSeparator,
    VisibleLargeSeparator,
    VisibleSmallSeparator,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from bot import Cordex

from constants import (
    ACCEPTED_EMOJI,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
)
from core import exceptions as e
from core.responses import multi_custom_message, send_custom_message
from events.messages.on_edit import MessageEditHandler

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_misc_sync() -> None:
    _ = await tree.sync()

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_misc_eval(bot : "Cordex", ctx : Context, body : str) -> None:
    env : dict[str, object] = {
        "bot"                  : bot,
        "ctx"                  : ctx,
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

        "discord"              : discord,
        "ui"                   : ui,

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
                raise e.AppBadArgument({"message-id" : "The message provided does not exist, I lack permissions to access it, or it is not a valid ID."}) from None

        if hasattr(channel, "typing"):
            async with channel.typing():
                await asyncio.sleep(typing_delay)

        if reply_reference:
            _ = await reply_reference.reply(content = text)
        else:
            _ = await channel.send(content = text)

        await interaction.followup.send("Sent!", ephemeral = True)

    except discord.Forbidden:
        raise e.AppUnknownError from None
