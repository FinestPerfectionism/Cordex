from typing import final, override

from discord import Role
from discord.abc import GuildChannel
from discord.ext import commands, tasks

from bot import Cordex
from core.moderation import Actions

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Quarantine Enforcing
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class QuarantineEnforcer(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot
        self.loop_quarantineenforce.start()

    @override
    async def cog_unload(self) -> None:
        self.loop_quarantineenforce.cancel()

    @tasks.loop(minutes = 10)
    async def loop_quarantineenforce(self) -> None:
        for guild in self.bot.guilds:
            actions = Actions(self.bot, guild)
            await actions.quarantine_enforce("Channel")
            await actions.quarantine_enforce("Role")

    @loop_quarantineenforce.before_loop
    async def beforeloop_quarantineenforce(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_guild_channel_update")
    async def listener_quarantineenforce_channelupdate(self, before : GuildChannel, after : GuildChannel) -> None:
        actions = Actions(self.bot, after.guild)
        quarantine_role = await actions.get_quarantine_role()

        if not quarantine_role:
            return

        if before.overwrites_for(quarantine_role) == after.overwrites_for(quarantine_role):
            return

        await actions.quarantine_enforce("Channel")

    @commands.Cog.listener("on_guild_channel_create")
    async def listener_quarantineenforce_channelcreate(self, before : GuildChannel, after : GuildChannel) -> None:
        actions = Actions(self.bot, after.guild)
        quarantine_role = await actions.get_quarantine_role()

        if not quarantine_role:
            return

        if before.overwrites_for(quarantine_role) == after.overwrites_for(quarantine_role):
            return

        await actions.quarantine_enforce("Channel")

    @commands.Cog.listener("on_guild_role_update")
    async def listener_quarantineenforce_roleupdate(self, before : Role, after : Role) -> None:
        if before.position == after.position:
            return

        actions = Actions(self.bot, after.guild)
        await actions.quarantine_enforce("Role")

async def setup(bot : Cordex) -> None:
    cog = QuarantineEnforcer(bot)
    await bot.add_cog(cog)
