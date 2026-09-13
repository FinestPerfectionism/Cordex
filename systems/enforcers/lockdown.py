from asyncio import gather
from typing import final, override

from discord import Guild
from discord.abc import GuildChannel
from discord.ext import commands, tasks

from bot import Cordex
from core.moderation import LockdownManager

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Lockdown Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class LockdownEnforcer(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot
        self.loop_lockdownenforce.start()

    @override
    async def cog_unload(self) -> None:
        self.loop_lockdownenforce.cancel()

    @tasks.loop(minutes = 10)
    async def loop_lockdownenforce(self) -> None:
        async def run_enforcement(guild : Guild) -> None:
            manager = LockdownManager(self.bot, guild)
            await manager.enforce()

        await gather(*(run_enforcement(guild) for guild in self.bot.guilds))

    @loop_lockdownenforce.before_loop
    async def beforeloop_lockdowneenforce(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_guild_channel_update")
    async def listener_lockdownenforce_channelupdate(self, _before : GuildChannel, after : GuildChannel) -> None:
        manager = LockdownManager(self.bot, after.guild)
        await manager.enforce()

    @commands.Cog.listener("on_guild_channel_create")
    async def listener_lockdownenforce_channelcreate(self, channel : GuildChannel) -> None:
        manager = LockdownManager(self.bot, channel.guild)
        await manager.enforce()

async def setup(bot : Cordex) -> None:
    cog = LockdownEnforcer(bot)
    await bot.add_cog(cog)
