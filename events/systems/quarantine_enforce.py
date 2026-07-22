from asyncio import Semaphore, gather, sleep
from typing import TYPE_CHECKING, final, override

from discord import Forbidden, HTTPException, PermissionOverwrite, Role
from discord.abc import GuildChannel
from discord.ext import commands, tasks

from bot import Cordex, log
from constants import MAIN_GUILD_ID, QUARANTINE_ROLE_ID

if TYPE_CHECKING:
    from collections.abc import Coroutine

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Quarantine Enforcement System
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class QuarantineEnforcerSystem(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot                   = bot
        self.semaphore             = Semaphore(3)
        self.processing : set[int] = set()
        self.loop_quarantine_enforce.start()

    @override
    async def cog_unload(self) -> None:
        self.loop_quarantine_enforce.cancel()

    def needs_update(self, channel : GuildChannel, role : Role) -> bool:
        overwrite = channel.overwrites_for(role)
        return (
            overwrite.view_channel             is not False or
            overwrite.create_instant_invite    is not False or
            overwrite.send_messages            is not False or
            overwrite.send_messages_in_threads is not False or
            overwrite.create_public_threads    is not False or
            overwrite.create_private_threads   is not False
        )

    async def update_channel(self, channel : GuildChannel, role : Role) -> bool:
        if channel.id in self.processing:
            return False

        self.processing.add(channel.id)
        async with self.semaphore:
            try:
                overwrite = PermissionOverwrite(
                    view_channel             = False,
                    create_instant_invite    = False,
                    send_messages            = False,
                    send_messages_in_threads = False,
                    create_public_threads    = False,
                    create_private_threads   = False,
                )
                await channel.set_permissions(role, overwrite = overwrite, reason = "Cordex Quarantine-Enforcement: fixing channel")
                log.info("Fixed quarantine permissions for role in channel/category: %s", channel.name)
                await sleep(0.25)
            except Forbidden:
                log.exception("Missing permissions to edit %s", channel.name)
            except HTTPException as e:
                if e.status == 429:
                    log.warning("Hit a 429 rate limit while editing %s. Backing off.", channel.name)
                else:
                    log.exception("Failed to edit %s", channel.name)
            finally:
                self.processing.remove(channel.id)

        return True

    @commands.Cog.listener("on_guild_channel_update")
    async def on_channel_update(self, _before : GuildChannel, after : GuildChannel) -> None:
        if after.guild.id != MAIN_GUILD_ID:
            return

        role = after.guild.get_role(QUARANTINE_ROLE_ID)
        if role and self.needs_update(after, role):
            await self.update_channel(after, role)

    @commands.Cog.listener("on_guild_channel_create")
    async def on_channel_create(self, channel : GuildChannel) -> None:
        if channel.guild.id != MAIN_GUILD_ID:
            return

        role = channel.guild.get_role(QUARANTINE_ROLE_ID)
        if role and self.needs_update(channel, role):
            await self.update_channel(channel, role)

    @tasks.loop(minutes = 10.0)
    async def loop_quarantine_enforce(self) -> None:
        log.info("Starting quarantine permissions enforcement.")
        guild = self.bot.get_guild(MAIN_GUILD_ID)
        if guild is None:
            return

        role = guild.get_role(QUARANTINE_ROLE_ID)
        if role is None:
            return

        all_channels : list[GuildChannel] = [*guild.categories, *guild.channels]
        tasks_to_run : list[Coroutine[None, None, bool]] = []

        tasks_to_run = [
            self.update_channel(channel, role)
            for channel in all_channels
            if self.needs_update(channel, role)
        ]

        if not tasks_to_run:
            log.info("Quarantine permissions enforcement finished. No channels needed changes.")
            return

        results : list[bool] = await gather(*tasks_to_run)
        channels_updated = sum(1 for r in results if r)

        if channels_updated > 0:
            log.info("Quarantine permissions enforcement finished. %s channels needed changes.", channels_updated)

    @loop_quarantine_enforce.before_loop
    async def waitloop_quarantine_enforce(self) -> None:
        await self.bot.wait_until_ready()

async def setup(bot : Cordex) -> None:
    cog = QuarantineEnforcerSystem(bot)
    await bot.add_cog(cog)
