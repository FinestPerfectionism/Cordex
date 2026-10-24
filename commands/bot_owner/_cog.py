from contextlib import suppress
from typing import final, override

from discord import Forbidden, HTTPException, Member, Message, Reaction, User
from discord.ext.commands import Cog
from discord.ext.commands import command as prefix_command

from bot import Context, Cordex
from core.exceptions import BadPermissionsPrefixCommand
from core.utilities import is_bot_owner

from .eval import run_botowner_eval
from .restart import run_botowner_restart
from .shutdown import run_botowner_shutdown
from .sql import run_botowner_sql
from .sync import run_botowner_sync

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class BotOwnerCommands(Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @override
    async def cog_check(self, ctx : Context) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        if not is_bot_owner(ctx.author):
            raise BadPermissionsPrefixCommand

        return True

    @Cog.listener("on_message_edit")
    async def listener_messageedit(self, before : Message, after : Message) -> None:
        author = before.author

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Process eval command edit.

        if self.bot.user and before.content != after.content:
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

    @Cog.listener("on_reaction_add")
    async def listener_reactionadd(self, reaction : Reaction, user : Member | User) -> None:
        message = reaction.message

        if not is_bot_owner(user):
            return

        if str(reaction.emoji) == "🗑️" and message.author == self.bot.user:
            with suppress(Exception):
                await message.delete()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "eval")
    async def cmd_botowner_eval(self, ctx : Context, *, body : str) -> None:
        await run_botowner_eval(ctx, body)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .restart Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "restart")
    async def cmd_botowner_restart(self, ctx : Context) -> None:
        await run_botowner_restart(ctx)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .shutdown Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "shutdown")
    async def cmd_botowner_shutdown(self, ctx : Context) -> None:
        await run_botowner_shutdown(ctx)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .sql Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "sql")
    async def cmd_botowner_sql(self, ctx : Context, *, body : str) -> None:
        await run_botowner_sql(ctx, body)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "sync")
    async def cmd_botowner_sync(self, ctx : Context) -> None:
        await run_botowner_sync(ctx)


async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
