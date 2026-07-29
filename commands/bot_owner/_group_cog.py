from typing import final

from discord import TextChannel
from discord.app_commands import Group, autocomplete, describe, rename
from discord.ext import commands
from discord.ext.commands import (  # type: ignore[reportMissingTypeStubs]
    command as prefix_command,
)

from bot import Context, Cordex, Interaction
from core.permissions import bot_owner_cmd

from . import cog_autocomplete
from .cogs import (
    run_bo_cog_load,
    run_bo_cog_pullreload,
    run_bo_cog_reload,
    run_bo_cog_unload,
)
from .eval import run_bo_eval
from .messages import run_bo_messages_delete, run_bo_messages_edit, run_bo_messages_send
from .state import run_bo_state_restart, run_bo_state_shutdown, run_bo_state_sync

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class BotOwnerCommands(
    commands.GroupCog,
    name        = "bot-owner",
    description = "Bot Owner only —— Bot owner commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    cog     : Group = Group(
        name        = "cog",
        description = "Bot owner cog commands",
    )
    message : Group = Group(
        name        = "message",
        description = "Bot owner message commands",
    )
    state   : Group = Group(
        name        = "state",
        description = "Bot owner state commands",
    )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog pull-reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "pull-reload",
        description = "Pull from main, then reload all cogs.",
    )
    @bot_owner_cmd()
    async def cmd_bo_cog_pullreload(self, interaction : Interaction) -> None:
        await run_bo_cog_pullreload(self.bot, interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "reload",
        description = "Reload a cog or all cogs.",
    )
    @describe(cog = "The cog to reload. Leave empty to reload all cogs.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_cog_reload(self, interaction : Interaction, cog : str | None) -> None:
        await run_bo_cog_reload(self.bot, interaction, cog)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog load Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "load",
        description = "Load a cog.",
    )
    @describe(cog = "The cog to load.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_cog_load(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cog_load(self.bot, interaction, cog)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog unload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "unload",
        description = "Unload a cog.",
    )
    @describe(cog = "The cog to unload.")
    @autocomplete(cog = cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_cog_unload(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cog_unload(self.bot, interaction, cog)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state shutdown Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "shutdown",
        description = "Shutdown the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_shutdown(self, interaction : Interaction) -> None:
        await run_bo_state_shutdown(self.bot, interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state restart Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "restart",
        description = "Restart the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_restart(self, interaction : Interaction) -> None:
        await run_bo_state_restart(self.bot, interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "sync",
        description = "Sync the bot tree.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_sync(self, interaction : Interaction) -> None:
        await run_bo_state_sync(self.bot, interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "eval")
    async def cmd_bo_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_eval(self.bot, ctx, body)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner message send Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @message.command(
        name        = "send",
        description = "Make the bot send something.",
    )
    @describe(
        text     = "The text to send.",
        reply_id = "The ID of the message to reply to.",
        channel  = "The channel to send the message in.",
        ping     = "Whether to mention the user upon replying. Does nothing if reply-id is None.",
    )
    @rename(reply_id = "reply-id")
    @bot_owner_cmd()
    async def cmd_bo_messages_send(
        self,
        interaction : Interaction,
        text        : str,
        reply_id    : str         | None = None,
        channel     : TextChannel | None = None,
        *,
        ping        : bool        | None = True,
    ) -> None:
        await run_bo_messages_send(
            interaction,
            text,
            reply_id,
            channel,
            ping = ping,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner message edit Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @message.command(
        name        = "edit",
        description = "Make the bot edit one of its own messages.",
    )
    @describe(
        text       = "The new text for the message.",
        message_id = "The ID of the message to edit.",
        channel    = "The channel where the message is located.",
    )
    @rename(message_id = "message-id")
    @bot_owner_cmd()
    async def cmd_bo_messages_edit(
        self,
        interaction : Interaction,
        text        : str,
        message_id  : str,
        channel     : TextChannel | None = None,
    ) -> None:
        await run_bo_messages_edit(
            interaction,
            text,
            message_id,
            channel,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner message delete Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @message.command(
        name        = "delete",
        description = "Make the bot delete one of its own messages.",
    )
    @describe(
        message_id = "The ID of the message to delete.",
        channel    = "The channel where the message is located.",
    )
    @rename(message_id = "message-id")
    @bot_owner_cmd()
    async def cmd_bo_messages_delete(
        self,
        interaction : Interaction,
        message_id  : str,
        channel     : TextChannel | None = None,
    ) -> None:
        await run_bo_messages_delete(
            interaction,
            message_id,
            channel,
        )

async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
