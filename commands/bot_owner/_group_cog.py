from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import final

from discord import Forbidden, HTTPException, Member, Message, Reaction, User
from discord.app_commands import Group, check
from discord.ext import commands
from discord.ext.commands import (  # pyright: ignore[reportMissingTypeStubs]
    command as prefix_command,
)

from bot import Context, Cordex, Interaction
from core.exceptions import BadPermissionsCommand
from core.state import unrestrictable
from core.utilities import is_bot_owner

from .eval import run_bo_eval
from .state import run_bo_state_restart, run_bo_state_shutdown, run_bo_state_sync


def bot_owner_cmd[F : Callable[..., Awaitable[None]]](func : F) -> F:
    def predicate(interaction : Interaction) -> bool:
        if is_bot_owner(interaction.user):
            return True

        raise BadPermissionsCommand

    return check(predicate)(func)

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

    state   : Group = Group(
        name        = "state",
        description = "Bot owner state commands.",
    )
    style   : Group = Group(
        name        = "style",
        description = "Bot owner style commands.",
    )

    @commands.Cog.listener("on_message_edit")
    async def listener_cmdeval_messageedit(self, before : Message, after : Message) -> None:
        author = before.author

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Process eval command edit.

        if after.content.startswith(".eval") and self.bot.user and before.content != after.content:
            try:
                await after.clear_reactions()
            except Forbidden:
                with suppress(HTTPException):
                    message = await after.channel.fetch_message(after.id)
                    for reaction in message.reactions:
                        if reaction.me:
                            await reaction.remove(self.bot.user)
            except HTTPException:
                pass

            await self.bot.process_commands(after)

    @commands.Cog.listener("on_reaction_add")
    async def listener_cmdeval_reactionadd(self, reaction : Reaction, user : Member | User) -> None:
        message = reaction.message

        if not is_bot_owner(user):
            return

        if str(reaction.emoji) == "🗑️" and message.author == self.bot.user:
            with suppress(Exception):
                await message.delete()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state shutdown Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "shutdown",
        description = "Shutdown the bot.",
    )
    @bot_owner_cmd
    async def cmd_bo_state_shutdown(self, interaction : Interaction) -> None:
        await run_bo_state_shutdown(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state restart Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "restart",
        description = "Restart the bot.",
    )
    @bot_owner_cmd
    async def cmd_bo_state_restart(self, interaction : Interaction) -> None:
        await run_bo_state_restart(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "sync",
        description = "Sync the bot tree.",
    )
    @bot_owner_cmd
    async def cmd_bo_state_sync(self, interaction : Interaction) -> None:
        await run_bo_state_sync(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "eval")
    async def cmd_bo_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_eval(ctx, body)


async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
