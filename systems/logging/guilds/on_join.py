from typing import Self, final

from discord import AllowedMentions, Guild, TextChannel
from discord.ext import commands

from bot import Cordex
from bot.ui import (
    Container,
    FallbackThumbnailSection,
    LayoutView,
    TextDisplay,
    Thumbnail,
)
from constants import BOT_GUILD_LOG_CHANNEL_ID, COLOR_GREEN
from core.utilities import format_now, format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Guild Join Logging
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class GuildJoinLogging(commands.Cog):
    """Logs when the bot is added to a guild."""

    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    async def _listener_guild_guildjoin(self, guild : Guild) -> None:
        owner = guild.owner or await self.bot.fetch_user(guild.owner_id) if guild.owner_id else None
        if not owner:
            return

        @final
        class JoinView(LayoutView):
            container = Container[Self](
                TextDisplay(f"# Joined Guild | {format_now("F")}"),
                FallbackThumbnailSection(
                    format_table(
                        {
                            "Owner"          : f"{owner.mention} | {owner.id}",
                            "Members"        : len(guild.members),
                            "Current Guilds" : len(self.bot.guilds),
                            "Current Users"  : len(self.bot.users),
                        },
                    ),
                    thumbnail = Thumbnail[Self](guild.icon.url) if guild.icon else None,
                ),
                color = COLOR_GREEN,
            )

        log_channel = self.bot.get_channel(BOT_GUILD_LOG_CHANNEL_ID) or await self.bot.fetch_channel(BOT_GUILD_LOG_CHANNEL_ID)

        if not isinstance(log_channel, TextChannel):
            return

        await log_channel.send(
            view             = JoinView(),
            allowed_mentions = AllowedMentions.none(),
        )


async def setup(bot : Cordex) -> None:  # ruff: ignore[undocumented-public-function]
    cog = GuildJoinLogging(bot)
    await bot.add_cog(cog)
