from discord.abc import GuildChannel
from discord.app_commands import command, describe, guild_only
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import administrator_cmd

from .info import run_channel_info

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Channel Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@guild_only
class ChannelCommands(
    commands.GroupCog,
    name        = "channel",
    description = "Administrators only — Channel commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /channel info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "info",
        description = "View information for a channel.",
    )
    @describe(channel = "The channel to view information for. Defaults to the current one.")
    @administrator_cmd()
    async def cmd_info(self, interaction : Interaction, channel : GuildChannel | None = None) -> None:
        await run_channel_info(interaction, channel)

async def setup(bot : Cordex) -> None:
    cog = ChannelCommands(bot)
    await bot.add_cog(cog)
