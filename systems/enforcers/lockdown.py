from typing import final, override

from discord.abc import GuildChannel
from discord.ext import commands, tasks

from bot import Cordex
from core.moderation import LockdownManager

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Lockdown Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class LockdownEnforcer(commands.Cog):
    """Enforces lockdowns by ensuring specific channel permissions."""

    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot
        self._loop_lockdownenforce.start()

    @override
    async def cog_unload(self) -> None:
        self._loop_lockdownenforce.cancel()

    @tasks.loop(minutes = 10)
    async def _loop_lockdownenforce(self) -> None:
        for guild in self.bot.guilds:
            manager = LockdownManager(self.bot, guild)
            await manager.enforce()

    @_loop_lockdownenforce.before_loop
    async def _beforeloop_lockdowneenforce(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_guild_channel_update")
    async def _listener_lockdownenforce_channelupdate(self, _before : GuildChannel, after : GuildChannel) -> None:
        manager = LockdownManager(self.bot, after.guild)
        await manager.enforce()

    @commands.Cog.listener("on_guild_channel_create")
    async def _listener_lockdownenforce_channelcreate(self, channel : GuildChannel) -> None:
        manager = LockdownManager(self.bot, channel.guild)
        await manager.enforce()


async def setup(bot : Cordex) -> None:
    cog = LockdownEnforcer(bot)
    await bot.add_cog(cog)
