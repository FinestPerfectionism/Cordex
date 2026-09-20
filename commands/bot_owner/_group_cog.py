from typing import final

from discord import Forbidden, HTTPException, Message
from discord.app_commands import Group, describe
from discord.ext import commands
from discord.ext.commands import (  # pyright: ignore[reportMissingTypeStubs]
    command as prefix_command,
)

from bot import Context, Cordex, Interaction
from core.permissions import bot_owner_cmd
from core.state import unrestrictable

from .eval import run_bo_eval
from .state import run_bo_state_restart, run_bo_state_shutdown, run_bo_state_sync
from .style import run_bo_style_reset, run_bo_style_set

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
@unrestrictable
class BotOwnerCommands(
    commands.GroupCog,
    name        = "bot-owner",
    description = "Bot Owner only —— Bot owner commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot  = bot
        self.tree = bot.tree

    message : Group = Group(
        name        = "message",
        description = "Bot owner message commands.",
    )
    state   : Group = Group(
        name        = "state",
        description = "Bot owner state commands.",
    )
    style   : Group = Group(
        name        = "style",
        description = "Bot owner style commands.",
    )

    @commands.Cog.listener("on_message_edit")
    async def cmd_eval_listener(self, before : Message, after : Message) -> None:
        author = before.author

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Process eval command edit.

        if after.content.startswith(".eval") and self.bot.user and before.content != after.content:
            try:
                await after.clear_reactions()
            except Forbidden:
                try:
                    message = await after.channel.fetch_message(after.id)
                    for reaction in message.reactions:
                        if reaction.me:
                            await reaction.remove(self.bot.user)
                except HTTPException:
                    pass
            except HTTPException:
                pass

            await self.bot.process_commands(after)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state shutdown Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "shutdown",
        description = "Shutdown the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_shutdown(self, interaction : Interaction) -> None:
        await run_bo_state_shutdown(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state restart Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "restart",
        description = "Restart the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_restart(self, interaction : Interaction) -> None:
        await run_bo_state_restart(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "sync",
        description = "Sync the bot tree.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_sync(self, interaction : Interaction) -> None:
        await run_bo_state_sync(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "eval")
    async def cmd_bo_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_eval(ctx, body)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner style reset Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @style.command(
        name        = "reset",
        description = "Reset the bot's server specific display name style.",
    )
    @describe(branded = "Whether the reset should be the bot's branding instead of normal font. Defaults to True.")
    async def cmd_bo_style_reset(self, interaction : Interaction, *, branded : bool | None = None) -> None:
        await run_bo_style_reset(
            interaction = interaction,
            branded     = branded,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner style set Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @style.command(
        name        = "set",
        description = "Set the bot's server specific display name style.",
    )
    @bot_owner_cmd()
    async def cmd_bo_style_set(self, interaction : Interaction) -> None:
        await run_bo_style_set(interaction)


async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
