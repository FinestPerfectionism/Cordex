from typing import TYPE_CHECKING, final

from discord.app_commands import Choice, choices, command, describe, guild_only, rename
from discord.ext import commands

from core.utilities import unimplemented

from .compare import run_channel_compare
from .duplicate import run_channel_duplicate
from .info import run_channel_info
from .permissions import run_channel_permissions
from .sync import run_channel_sync

if TYPE_CHECKING:
    from discord.abc import GuildChannel

    from bot import Cordex, Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Channel Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
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

    @command(
        name        = "sync",
        description = "Sync a channel's permissions to it's category. Defaults to the current one.",
    )
    @describe(channel = "The channel to sync permissions for. Defaults to the current one.")
    async def cmd_channel_sync(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_channel_sync(interaction, channel)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /channel duplicate Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "duplicate",
        description = "Duplicate a channel or category.",
    )
    @describe(channel = "The channel to duplicate. Defaults to the current one.")
    @unimplemented()
    async def cmd_channel_duplicate(
        self,
        interaction : Interaction,
        channel     : GuildChannel | None = None,
    ) -> None:
        await run_channel_duplicate(interaction, channel)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /channel compare Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "compare",
        description = "List all differing permissions for two selected channels.",
    )
    @rename(
        channel_1 = "channel-1",
        channel_2 = "channel-2",
    )
    @describe(
        channel_1 = "The first channel to compare.",
        channel_2 = "The second channel to compare.",
    )
    @unimplemented()
    async def cmd_channel_compare(
        self,
        interaction : Interaction,
        channel_1   : GuildChannel | None = None,
        channel_2   : GuildChannel | None = None,
    ) -> None:
        await run_channel_compare(interaction, channel_1, channel_2)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /channel permissions Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "permissions",
        description = "List permissions for a selected channel.",
    )
    @rename(permissions_filter = "filter")
    @describe(
        channel     = "The channel to list permissions for.",
        permissions_filter = "Whether to show enabled or disabled permissions. Defaults to both.",
    )
    @choices(
        permissions_filter = [
            Choice(name = "Enabled",  value = "enabled"),
            Choice(name = "Disabled", value = "disabled"),
        ],
    )
    @unimplemented()
    async def cmd_channel_permissions(
        self,
        interaction        : Interaction,
        channel            : GuildChannel | None = None,
        permissions_filter : str          | None = None,
    ) -> None:
        await run_channel_permissions(interaction, channel, permissions_filter)

# async def setup(bot : Cordex) -> None:
#     cog = ChannelCommands(bot)
#     await bot.add_cog(cog)
