from typing import final

from discord import Guild
from discord.ext import commands

from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Style Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class StyleEnforcer(commands.Cog):
    """Sets the bot's name style upon joining a guild."""

    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    async def _listener_styleenforce_guildjoin(self, guild : Guild) -> None:
        await self.bot.reset_name_style(guild)


async def setup(bot : Cordex) -> None:  # ruff: ignore[undocumented-public-function]
    cog = StyleEnforcer(bot)
    await bot.add_cog(cog)
