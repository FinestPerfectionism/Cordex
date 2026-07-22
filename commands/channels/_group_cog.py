from typing import final

from discord.abc import GuildChannel
from discord.app_commands import command, describe, guild_only
from discord.ext import commands

from bot import Cordex, Interaction
from core.help import help_description
from core.permissions import administrator_cmd

from .duplicate import run_channel_duplicate
from .info import run_channel_info
from .sync import run_channel_sync

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Channel Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@guild_only
@final
class ChannelCommands(
    commands.GroupCog,
    name        = "channel",
    description = "Channel commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /channel info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"channel" : "The channel to view information for. Defaults to the current one."})
    @command(
        name        = "info",
        description = "View information for a channel.",
    )
    @describe(channel = "The channel to view information for. Defaults to the current one.")
    async def cmd_channel_info(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_channel_info(interaction, channel)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /channel sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"channel" : "The channel to sync permissions for. Defaults to the current one."})
    @command(
        name        = "sync",
        description = "Sync a channel's permissions to it's category. Defaults to the current one.",
    )
    @describe(channel = "The channel to sync permissions for. Defaults to the current one.")
    @administrator_cmd()
    async def cmd_channel_sync(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_channel_sync(interaction, channel)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /channel duplicate Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"channel" : "The channel to duplicate. Defaults to the current one."})
    @command(
        name        = "duplicate",
        description = "Duplicate a channel or category.",
    )
    @describe(channel = "The channel to duplicate. Defaults to the current one.")
    @administrator_cmd()
    async def cmd_channel_duplicate(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_channel_duplicate(interaction, channel)

async def setup(bot : Cordex) -> None:
    cog = ChannelCommands(bot)
    await bot.add_cog(cog)
