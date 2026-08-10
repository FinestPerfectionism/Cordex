from typing import final, override

from discord import Member
from discord.ext import commands, tasks

from bot import Cordex
from constants import MAIN_GUILD_ID, PERSONAL_LEAVE_ROLE_ID

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Leave Enforcement System
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class LeaveEnforcerSystem(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot = bot

    @override
    async def cog_load(self) -> None:
        self.loop_leave_enforce.start()

    @override
    async def cog_unload(self) -> None:
        self.loop_leave_enforce.cancel()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Internal Helpers
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Event Listeners (Fast track loop for member update)
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.Cog.listener("on_member_update")
    async def listen_leave_enforce(self, before : Member, after : Member) -> None:
        guild = self.bot.get_guild(MAIN_GUILD_ID)
        if guild is None:
            return

        role = guild.get_role(PERSONAL_LEAVE_ROLE_ID)
        if role is None:
            return

        if before.nick == after.nick and before.roles == after.roles:
            return

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Loop
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @tasks.loop(minutes = 1)
    async def loop_leave_enforce(self) -> None:
        ...

    @loop_leave_enforce.before_loop
    async def waitloop_leave_enforce(self) -> None:
        await self.bot.wait_until_ready()

async def setup(bot : Cordex) -> None:
    cog = LeaveEnforcerSystem(bot)
    await bot.add_cog(cog)
