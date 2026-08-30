from typing import TYPE_CHECKING, final

from discord.ext import commands

if TYPE_CHECKING:
    from discord import Guild

    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Style Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class StyleEnforcer(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    async def style_enforcer(self, guild : Guild) -> None:
        await self.bot.reset_name_style(guild)

async def setup(bot : Cordex) -> None:
    cog = StyleEnforcer(bot)
    await bot.add_cog(cog)
