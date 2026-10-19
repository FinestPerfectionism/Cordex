from contextlib import suppress
from typing import final, override

from discord import HTTPException
from discord.abc import GuildChannel
from discord.ext.commands import Cog
from discord.ext.tasks import loop

from bot import Cordex
from bot.types import GuildMessagableChannel
from core.moderation import LockdownManager
from core.moderation.cases import CasesManager
from core.moderation.payloads import LockdownRemovePayload

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Lockdown Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class LockdownEnforcer(Cog):
    """Enforces lockdowns by ensuring specific channel permissions are configured properly."""

    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot
        self._loop_lockdownenforce.start()

    @override
    async def cog_unload(self) -> None:
        self._loop_lockdownenforce.cancel()

    @loop(minutes = 10)
    async def _loop_lockdownenforce(self) -> None:
        for guild in self.bot.guilds:
            manager = LockdownManager(self.bot, guild)
            try:
                await manager.enforce()
            except HTTPException as e:
                if e.status == 429:
                    break

    @_loop_lockdownenforce.before_loop
    async def _beforeloop_lockdownenforce(self) -> None:
        await self.bot.wait_until_ready()

    @Cog.listener("on_guild_channel_update")
    async def _listener_lockdownenforce_channelupdate(self, before : GuildChannel, after : GuildChannel) -> None:
        if before.overwrites == after.overwrites:
            return

        everyone = after.guild.default_role
        if after.overwrites_for(everyone).send_messages is False:
            return

        manager = LockdownManager(self.bot, after.guild)
        if after.id in await manager.get_channels(by_id = True):
            with suppress(HTTPException):
                await manager.enforce()

    @Cog.listener("on_guild_channel_delete")
    async def _listener_lockdownenforce_channeldelete(self, channel : GuildChannel) -> None:
        if not isinstance(channel, GuildMessagableChannel):
            return

        guild   = channel.guild
        manager = LockdownManager(self.bot, guild)
        if channel.id not in await manager.get_channels(by_id = True):
            return

        await self.bot.db.execute(
            t"DELETE FROM Lockdowns WHERE channel_id = {channel.id} AND guild_id = {guild.id}",
        )
        await self.bot.db.commit()

        payload = LockdownRemovePayload(
            moderator = guild.me,
            channel   = channel,
            reason    = "The channel was deleted.",
        )
        await CasesManager(self.bot, guild).create_case(payload)


async def setup(bot : Cordex) -> None:  # ruff: ignore[undocumented-public-function]
    cog = LockdownEnforcer(bot)
    await bot.add_cog(cog)
