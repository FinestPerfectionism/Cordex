from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import final

from discord import Forbidden, HTTPException, Member, Message, Reaction, User
from discord.ext import commands
from discord.ext.commands import (  # pyright: ignore[reportMissingTypeStubs]
    command as prefix_command,
)

from bot import Context, Cordex
from core.exceptions import PrefixBadPermissionsCommand
from core.utilities import is_bot_owner

from .eval import run_bo_eval
from .restart import run_bo_restart
from .shutdown import run_bo_shutdown
from .sync import run_bo_sync


def bot_owner_cmd[F : Callable[..., Awaitable[None]]](func : F) -> F:
    def predicate(ctx : Context) -> bool:
        if is_bot_owner(ctx.author):
            return True

        raise PrefixBadPermissionsCommand

    return commands.check(predicate)(func)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class BotOwnerCommands(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

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
    # .shutdown Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "shutdown")
    @bot_owner_cmd
    async def cmd_bo_shutdown(self, ctx : Context) -> None:
        await run_bo_shutdown(ctx)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .restart Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "restart")
    @bot_owner_cmd
    async def cmd_bo_restart(self, ctx : Context) -> None:
        await run_bo_restart(ctx)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "sync")
    @bot_owner_cmd
    async def cmd_bo_sync(self, ctx : Context) -> None:
        await run_bo_sync(ctx)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "eval")
    @bot_owner_cmd
    async def cmd_bo_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_eval(ctx, body)


async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
