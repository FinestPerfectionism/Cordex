from typing import TYPE_CHECKING

from discord import TextChannel
from discord.app_commands import autocomplete, command, describe, rename
from discord.ext import commands
from discord.ext.commands import (  # type: ignore[reportMissingTypeStubs]
    command as prefix_command,
)

from bot import Context, Cordex, Interaction, log
from core.permissions import bot_owner_cmd

from . import cog_autocomplete, get_cogs
from .cogs import (
    run_bo_cogs_load,
    run_bo_cogs_pullreload,
    run_bo_cogs_reload,
    run_bo_cogs_unload,
)
from .eval import run_bo_eval
from .messages import run_bo_messages_delete, run_bo_messages_edit, run_bo_messages_send
from .state import run_bo_state_restart, run_bo_state_shutdown, run_bo_state_sync

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
        self.bot        : Cordex     = bot
        self.logger     : Logger     = log
        self.restarting : list[bool] = [False]

    @property
    def cogs(self) -> list[str]:
        return get_cogs()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner pull-reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "pull-reload",
        description = "Pull from main, then reload all cogs.",
    )
    @bot_owner_cmd()
    async def cmd_bo_pullreload(self, interaction : Interaction) -> None:
        await run_bo_cogs_pullreload(self.bot, interaction, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "reload",
        description = "Reload a cog or all cogs.",
    )
    @describe(cog = "The cog to reload. Leave empty to reload all cogs.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_reload(self, interaction : Interaction, cog : str | None) -> None:
        await run_bo_cogs_reload(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner load Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "load",
        description = "Load a cog.",
    )
    @describe(cog = "The cog to load.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_load(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cogs_load(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner unload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "unload",
        description = "Unload a cog.",
    )
    @describe(cog = "The cog to unload.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_unload(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cogs_unload(self.bot, interaction, cog, get_cogs())

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner shutdown Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "shutdown",
        description = "Shutdown the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_shutdown(self, interaction : Interaction) -> None:
        await run_bo_state_shutdown(self.bot, interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner restart Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "restart",
        description = "Restart the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_restart(self, interaction : Interaction) -> None:
        await run_bo_state_restart(self.bot, interaction, self.restarting, self.logger)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "sync",
        description = "Sync the bot tree.",
    )
    @bot_owner_cmd()
    async def cmd_bo_sync(self, interaction : Interaction) -> None:
        await run_bo_state_sync(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "eval")
    async def cmd_bo_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_eval(self.bot, ctx, body)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner send Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "send",
        description = "Make the bot send something.",
    )
    @describe(
        message  = "The text to send.",
        channel  = "The channel to send the message in.",
        reply_id = "The ID of the message to reply to.",
        ping     = "Whether to mention the user upon replying. Does nothing if reply-id is None.",
    )
    @rename(reply_id = "reply-id")
    @bot_owner_cmd()
    async def cmd_bo_send(
        self,
        interaction : Interaction,
        message     : str,
        channel     : TextChannel | None = None,
        reply_id    : str         | None = None,
        *,
        ping        : bool        | None = True,
    ) -> None:
        await run_bo_messages_send(
            interaction = interaction,
            channel     = channel,
            text        = message,
            message_id  = reply_id,
            ping        = ping,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner edit Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "edit",
        description = "Make the bot edit one of its own messages.",
    )
    @describe(
        message_id = "The ID of the message to edit.",
        message    = "The new text for the message.",
        channel    = "The channel where the message is located.",
    )
    @rename(
        message_id = "message-id",
        channel    = "target-channel",
    )
    @bot_owner_cmd()
    async def cmd_bo_edit(
        self,
        interaction : Interaction,
        message_id  : str,
        message     : str,
        channel     : TextChannel | None = None,
    ) -> None:
        await run_bo_messages_edit(
            interaction = interaction,
            channel     = channel,
            text        = message,
            message_id  = message_id,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner delete Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "delete",
        description = "Make the bot delete one of its own messages.",
    )
    @describe(
        message_id = "The ID of the message to delete.",
        channel    = "The channel where the message is located.",
    )
    @rename(
        message_id = "message-id",
        channel    = "target-channel",
    )
    @bot_owner_cmd()
    async def cmd_bo_delete(
        self,
        interaction : Interaction,
        message_id  : str,
        channel     : TextChannel | None = None,
    ) -> None:
        await run_bo_messages_delete(
            interaction = interaction,
            channel     = channel,
            message_id  = message_id,
        )

async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
