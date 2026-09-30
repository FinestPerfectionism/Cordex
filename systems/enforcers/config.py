from typing import final, override

from discord import Guild
from discord.ext import commands, tasks

from bot import Cordex, log

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Configuration Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class ConfigEnforcer(commands.Cog):
    """Resets configurations when the bot leaves or when the bot is (possibly due to the bot leaving while offline)."""

    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot
        self._loop_configenforce.start()

    async def _get_configured_guilds(self) -> set[int]:
        async with self.bot.db.execute(t"SELECT DISTINCT guild_id FROM Config;") as cursor:
            rows = await cursor.fetchall()
            return {row[0] for row in rows}

    @override
    async def cog_unload(self) -> None:
        self._loop_configenforce.cancel()

    @tasks.loop(minutes = 10)
    async def _loop_configenforce(self) -> None:
        configured_guild_ids = await self._get_configured_guilds()
        true_guild_ids       = {guild.id for guild in self.bot.guilds}
        stale_guild_ids      = [guild_id for guild_id in configured_guild_ids if guild_id not in true_guild_ids]

        reset = 0
        if stale_guild_ids:
            try:
                await self.bot.db.execute(t"DELETE FROM Config WHERE guild_id IN {tuple(stale_guild_ids)}")
                await self.bot.db.commit()
            except Exception:
                log.exception("An exception occurred during the configuration resets. Moving on.")
            else:
                reset = len(stale_guild_ids)

        if reset > 0:
            log.info("Configuration reset complete. %s guilds reset.", reset)

    @_loop_configenforce.before_loop
    async def _beforeloop_configenforce(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_guild_leave")
    async def _listener_config_guildleave(self, guild : Guild) -> None:
        await self.bot.config(guild).reset()


async def setup(bot : Cordex) -> None:  # ruff: ignore[undocumented-public-function]
    cog = ConfigEnforcer(bot)
    await bot.add_cog(cog)
