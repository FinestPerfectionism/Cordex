from typing import final

from discord.ext import commands

from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Configuration Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class ConfigEnforcer(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_guild_leave")
    async def listener_config_onguildleave() -> None:
        ...

async def setup(bot : Cordex) -> None:
    cog = ConfigEnforcer(bot)
    await bot.add_cog(cog)
