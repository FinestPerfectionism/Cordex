from asyncio import gather
from typing import final, override

from discord import Guild, Role
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
        async def run_enforcement(guild : Guild) -> None:
            actions = Actions(self.bot, guild)
            await actions.quarantine_enforce("Channel")
            await actions.quarantine_enforce("Role")

        await gather(*(run_enforcement(guild) for guild in self.bot.guilds))

    @loop_quarantineenforce.before_loop
    async def beforeloop_quarantineenforce(self) -> None:
        await self.bot.wait_until_ready()

    @commands.Cog.listener("on_guild_channel_update")
    async def listener_quarantineenforce_channelupdate(self, before : GuildChannel, after : GuildChannel) -> None:
        actions = Actions(self.bot, after.guild)
        quarantine_role = await actions.get_quarantine_role()

        if not quarantine_role:
            return

        before_ow = before.overwrites_for(quarantine_role)
        after_ow  = after.overwrites_for(quarantine_role)

        if before_ow == after_ow:
            return

        expected_send = False
        expected_read = False
        if (
            after_ow.send_messages == expected_send
            and after_ow.read_messages == expected_read
            and after_ow.send_messages_in_threads == expected_send
            and after_ow.create_public_threads == expected_send
            and after_ow.create_private_threads == expected_send
            and after_ow.create_instant_invite == expected_send
        ):
            return

        await actions.quarantine_enforce("Channel")

    @commands.Cog.listener("on_guild_channel_create")
    async def listener_quarantineenforce_channelcreate(self, channel : GuildChannel) -> None:
        actions = Actions(self.bot, channel.guild)
        quarantine_role = await actions.get_quarantine_role()

        if not quarantine_role:
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
