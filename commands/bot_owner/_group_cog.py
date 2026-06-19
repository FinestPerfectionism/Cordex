from typing import TYPE_CHECKING

from discord import TextChannel
from discord.abc import Messageable
from discord.app_commands import autocomplete, describe, rename
from discord.app_commands import command as app_command
from discord.ext import commands

from bot import Context, Cordex, Interaction, log
from core.permissions import bot_owner_cmd

from ._base import cog_autocomplete, get_cogs
from .cogs import (
    run_bo_cogs_load,
    run_bo_cogs_pullreload,
    run_bo_cogs_reload,
    run_bo_cogs_unload,
)
from .messages import run_bo_messages_delete, run_bo_messages_edit, run_bo_messages_send
from .misc import run_bo_misc_eval, run_bo_misc_sync
from .state import run_bo_state_restart, run_bo_state_shutdown

if TYPE_CHECKING:
    from logging import Logger

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BotOwnerCommands(
    commands.GroupCog,
    name        = "bot-owner",
    description = "Bot Owner only —— Bot owner commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot            :  Cordex    = bot
        self.logger         : Logger     = log
        self.restarting_ref : list[bool] = [False]

    @property
    def cogs(self) -> list[str]:
        return get_cogs()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner pull-reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "pull-reload",
        description = "Pull from main, then reload all cogs.",
    )
    @bot_owner_cmd()
    async def cmd_pullreload(self, interaction : Interaction) -> None:
        await run_bo_cogs_pullreload(self.bot, interaction, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "reload",
        description = "Reload a cog or all cogs.",
    )
    @describe(cog = "The cog to reload. Leave empty to reload all cogs.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_reload(self, interaction : Interaction, cog : str | None) -> None:
        await run_bo_cogs_reload(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner load Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "load",
        description = "Load a cog.",
    )
    @describe(cog = "The cog to load.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_load(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cogs_load(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner unload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "unload",
        description = "Unload a cog.",
    )
    @describe(cog = "The cog to unload.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_unload(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cogs_unload(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .shutdown/.shut Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "shutdown", aliases = ["shut"])
    @bot_owner_cmd()
    async def cmd_shutdown(self, ctx : Context) -> None:
        await run_bo_state_shutdown(self.bot, ctx)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .restart/.r Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "restart", aliases = ["r"])
    @bot_owner_cmd()
    async def cmd_restart(self, ctx : Context) -> None:
        await run_bo_state_restart(self.bot, ctx, self.restarting_ref, self.logger)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "sync")
    @bot_owner_cmd()
    async def cmd_sync(self, ctx : Context) -> None:
        await run_bo_misc_sync(ctx)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "eval")
    @bot_owner_cmd()
    async def cmd_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_misc_eval(self.bot, ctx, body)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner send Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "send",
        description = "Make the bot send something.",
    )
    @describe(
        message        = "The text to send.",
        target_channel = "The channel to send the message in.",
        reply_id       = "The ID of the message to reply to.",
    )
    @rename(
        target_channel = "target-channel",
        reply_id       = "reply-id",
    )
    @bot_owner_cmd()
    async def cmd_messages_send(
        self,
        interaction    : Interaction,
        message        : str,
        target_channel : TextChannel | None = None,
        reply_id       : str         | None = None,
    ) -> None:
        target = target_channel or interaction.channel

        if not isinstance(target, Messageable):
            return

        await run_bo_messages_send(
            interaction = interaction,
            channel     = target,
            text        = message,
            message_id  = reply_id,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner edit Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "edit",
        description = "Make the bot edit one of its own messages.",
    )
    @describe(
        message_id     = "The ID of the message to edit.",
        message        = "The new text for the message.",
        target_channel = "The channel where the message is located.",
    )
    @rename(
        message_id     = "message-id",
        target_channel = "target-channel",
    )
    @bot_owner_cmd()
    async def cmd_messages_edit(
        self,
        interaction    : Interaction,
        message_id     : str,
        message        : str,
        target_channel : TextChannel | None = None,
    ) -> None:
        target = target_channel or interaction.channel

        if not isinstance(target, Messageable):
            return

        await run_bo_messages_edit(
            interaction = interaction,
            channel     = target,
            text        = message,
            message_id  = message_id,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner delete Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(
        name        = "delete",
        description = "Make the bot delete one of its own messages.",
    )
    @describe(
        message_id     = "The ID of the message to delete.",
        target_channel = "The channel where the message is located.",
    )
    @rename(
        message_id     = "message-id",
        target_channel = "target-channel",
    )
    @bot_owner_cmd()
    async def cmd_messages_delete(
        self,
        interaction    : Interaction,
        message_id     : str,
        target_channel : TextChannel | None = None,
    ) -> None:
        target = target_channel or interaction.channel

        if not isinstance(target, Messageable):
            return

        await run_bo_messages_delete(
            interaction = interaction,
            channel     = target,
            message_id  = message_id,
        )

async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
