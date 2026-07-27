from typing import final, override

from discord.ext import commands

from bot import Cordex
from constants import (
    HIERARCHY_CHANNEL_ID,
    PARTNERSHIP_REQUIREMENTS_CHANNEL_ID,
    PARTNERSHIPS_CHANNEL_ID,
    RULES_CHANNEL_ID,
    STAFF_LEAVE_CHANNEL_ID,
    TICKETS_CHANNEL_ID,
)
from guild_info import (
    HierarchyViewsList,
    PartnershipViewsList,
    RuleViewsList,
    ensure_views,
)
from guild_info.leave import LeaveComponents
from guild_info.partnerships import build_partnership_views
from guild_info.tickets import TicketComponents

from .state import load_partnership_data

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Core Guild Information Ensurement Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class CoreEnsurementHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @override
    async def cog_load(self) -> None:
        await self._ensure()

    async def _ensure(self) -> None:
        data = await load_partnership_data(self.bot.db)
        views, files = build_partnership_views(data["partnerships"])

        await ensure_views(
            bot        = self.bot,
            channel_id = HIERARCHY_CHANNEL_ID,
            views      = HierarchyViewsList,
        )

        await ensure_views(
            bot        = self.bot,
            channel_id = STAFF_LEAVE_CHANNEL_ID,
            views      = [LeaveComponents()],
        )
        self.bot.add_view(LeaveComponents())

        await ensure_views(
            bot        = self.bot,
            channel_id = TICKETS_CHANNEL_ID,
            views      = [TicketComponents()],
        )
        self.bot.add_view(TicketComponents())

        await ensure_views(
            bot        = self.bot,
            channel_id = PARTNERSHIPS_CHANNEL_ID,
            views      = views,
            files      = files,
        )

        await ensure_views(
            bot        = self.bot,
            channel_id = RULES_CHANNEL_ID,
            views      = RuleViewsList,
        )

        await ensure_views(
            bot        = self.bot,
            channel_id = PARTNERSHIP_REQUIREMENTS_CHANNEL_ID,
            views      = PartnershipViewsList,
        )

async def setup(bot : Cordex) -> None:
    cog = CoreEnsurementHandler(bot)
    await bot.add_cog(cog)
