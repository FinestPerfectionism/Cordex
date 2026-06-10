from typing import TYPE_CHECKING

import discord
from discord.app_commands import autocomplete, describe, rename
from discord.app_commands import command as app_command
from discord.ext import commands

from bot import Context, Interaction, log
from core.exceptions import UnknownError
from core.permissions import bot_owner_cmd

from ._base import cog_autocomplete, get_cogs
from .cogs.load import run_bo_cogs_load
from .cogs.pullreload import run_bo_cogs_pullreload
from .cogs.reload import run_bo_cogs_reload
from .cogs.unload import run_bo_cogs_unload
from .misc import run_bo_misc_eval, run_bo_misc_say, run_bo_misc_sync
from .state.restart import run_bo_state_restart
from .state.shutdown import run_bo_state_shutdown

if TYPE_CHECKING:
    from logging import Logger

    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class BotOwnerCommands(
    commands.GroupCog,
    name        = "bot-owner",
    description = "Bot Owner only —— Bot owner commands.",
):
    def __init__(self, bot : "Cordex") -> None:
        super().__init__()
        self.bot            : "Cordex"   = bot
        self.logger         : Logger     = log
        self.restarting_ref : list[bool] = [False]

    @property
    def cogs(self) -> list[str]:
        return get_cogs()

    @commands.command()
    @bot_owner_cmd()
    async def testing(self, _ctx : Context):
        raise UnknownError

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

    @app_command(description = "Reload a cog or all cogs.")
    @describe(cog = "The cog to reload. Leave empty to reload all cogs.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_reload(self, interaction : Interaction,  cog : str | None) -> None:
        await run_bo_cogs_reload(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner load Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(description = "Load a cog.")
    @describe(cog = "The cog to load.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_load(self, interaction : Interaction,  cog : str) -> None:
        await run_bo_cogs_load(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner unload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(description = "Unload a cog.")
    @describe(cog = "The cog to unload.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_unload(self, interaction : Interaction,  cog : str) -> None:
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
    async def cmd_sync(self, _ctx : Context) -> None:
        await run_bo_misc_sync()

   # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
   # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "eval")
    @bot_owner_cmd()
    async def cmd_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_misc_eval(self.bot, ctx, body)

   # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner say Command
   # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_command(description = "Make the bot say something.")
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
    async def cmd_say(
        self,
        interaction    : Interaction,
        message        : str,
        target_channel : discord.TextChannel | None = None,
        reply_id       : str                 | None = None,
    ) -> None:
        target = target_channel or interaction.channel

        if not isinstance(target, discord.abc.Messageable):
            return

        await run_bo_misc_say(
            interaction = interaction,
            channel     = target,
            text        = message,
            message_id  = reply_id,
        )

async def setup(bot : "Cordex") -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
