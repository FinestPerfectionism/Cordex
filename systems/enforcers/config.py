from typing import cast, final, override

from discord import Guild
from discord.ext import commands, tasks

from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Configuration Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class ConfigEnforcer(commands.Cog):
    """Resets configurations when the bot leaves or when the bot is (possibly due to the bot leaivng while offline)."""

    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot
        self._loop_configenforce.start()

    async def get_configured_guilds(self) -> set[int]:
        async with self.bot.db.execute(t"SELECT DISTINCT guild_id FROM Config;") as cursor:
            rows = await cursor.fetchall()
            return {cast("int", row[0]) for row in rows}

    @override
    async def cog_unload(self) -> None:
        self._loop_configenforce.cancel()

    @tasks.loop(minutes = 10)
    async def _loop_configenforce(self) -> None:
        configured_guild_ids = await self.get_configured_guilds()
        true_guild_ids       = {guild.id for guild in self.bot.guilds}

        for guild_id in configured_guild_ids:
            if guild_id not in true_guild_ids:
                await self.bot.config(self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)).reset()

    @_loop_configenforce.before_loop
    async def _beforeloop_configenforce(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_guild_leave")
    async def _listener_config_guildleave(self, guild : Guild) -> None:
        await self.bot.config(guild).reset()


async def setup(bot : Cordex) -> None:  # ruff: ignore[undocumented-public-function]
    cog = ConfigEnforcer(bot)
    await bot.add_cog(cog)
