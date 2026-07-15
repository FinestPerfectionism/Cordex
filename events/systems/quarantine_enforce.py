from asyncio import Semaphore, gather, sleep
from typing import TYPE_CHECKING, override

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

class QuarantineEnforcerSystem(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot       : Cordex    = bot
        self.semaphore : Semaphore = Semaphore(3)
        self.loop_quarantine_enforce.start()

    @override
    async def cog_unload(self) -> None:
        self.loop_quarantine_enforce.cancel()

    async def update_channel(self, channel : GuildChannel, role : Role, overwrite : PermissionOverwrite) -> bool:
        async with self.semaphore:
            try:
                overwrite.update(
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
            else:
                return True
            return False

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

        for channel in all_channels:
            current_overwrite = channel.overwrites_for(role)

            needs_update = (
                current_overwrite.view_channel             is not False or
                current_overwrite.create_instant_invite    is not False or
                current_overwrite.send_messages            is not False or
                current_overwrite.send_messages_in_threads is not False or
                current_overwrite.create_public_threads    is not False or
                current_overwrite.create_private_threads   is not False
            )

            if needs_update:
                tasks_to_run.append(self.update_channel(channel, role, current_overwrite))

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
