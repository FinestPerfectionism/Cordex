from asyncio import to_thread
from logging import getLogger as get_logger
from pathlib import Path
from typing import TypedDict, Unpack, override

from aiosqlite import Connection, connect
from discord import CustomActivity, Intents, Message, Status
from discord import Interaction as BaseInteraction
from discord.ext import commands
from discord.ext.commands import (  # type: ignore[reportMissingTypeStubs]
    Context as BaseContext,
)
from discord.ext.commands.view import StringView  # type: ignore[reportMissingTypeStubs]
from discord.ui import LayoutView, View

from constants import (
    HIERARCHY_CHANNEL_ID,
    PARTNERSHIP_REQUIREMENTS_CHANNEL_ID,
    PARTNERSHIPS_CHANNEL_ID,
    RULES_CHANNEL_ID,
    TICKETS_CHANNEL_ID,
)
from core.cog_loader import discover_cogs
from core.state.partnerships import load_partnership_data
from guild_info import (
    HierarchyViewsList,
    PartnershipViewsList,
    RuleViewsList,
    ensure_views,
)
from guild_info.partnerships import build_partnership_views
from guild_info.tickets import TicketComponents

from .ui import Inter, ViewButton

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot & Client Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

log = get_logger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Context and Interaction Classes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class ContextKwargs(TypedDict, total = False):
    message : Message
    bot     : "Cordex"
    view    : StringView

class ContextClass(BaseContext["Cordex"]):
    def __init__(self, **kwargs : Unpack[ContextKwargs]) -> None:
        super().__init__(**kwargs)

    async def send_button(self, callback : Inter) -> None:
        await self.send(view = ViewButton(callback))

    async def send_view(self, view : View | LayoutView) -> None:
        await self.send(view = view)


type Context     = ContextClass
type Interaction = BaseInteraction["Cordex"] | BaseInteraction

type ContextOrInteraction = Interaction | Context

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cordex Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Cordex(commands.Bot):
    def __init__(self) -> None:
        prefix   = commands.when_mentioned_or(".")
        intents  = Intents.all()
        status   = Status.online
        activity = CustomActivity(name = "Utility Bot 1.5.")

        super().__init__(
            command_prefix   = prefix,
            intents          = intents,
            case_insensitive = True,
            help_command     = None,
            status           = status,
            activity         = activity,
        )
        self.db : Connection

    @override
    async def get_context[ContextT : BaseContext[Cordex]](
        self,
        origin : Message        | BaseInteraction,
        *,
        cls    : type[ContextT] | None = None,
    ) -> ContextT | Context:
        return await super().get_context(origin, cls = cls or ContextClass)

    @override
    async def setup_hook(self) -> None:

        # ⸻ AIOSQLite

        db_path = Path("data/database.db")
        db_path.parent.mkdir(parents = True, exist_ok = True)

        self.db = await connect(str(db_path))

        def read_schemas() -> tuple[str, str, str, str, str]:
            with Path("schemas/logging.sql").open(encoding = "utf-8") as f1:
                log_sql = f1.read()
            with Path("schemas/cases.sql").open(encoding = "utf-8") as f2:
                cases_sql = f2.read()
            with Path("schemas/partnerships.sql").open(encoding = "utf-8") as f3:
                partnerships_sql = f3.read()
            with Path("schemas/guild_info.sql").open(encoding = "utf-8") as f4:
                guild_info_sql = f4.read()
            with Path("schemas/tickets.sql").open(encoding = "utf-8") as f5:
                tickets_sql = f5.read()
            return log_sql, cases_sql, partnerships_sql, guild_info_sql, tickets_sql

        logging_schema, cases_schema, partnerships_schema, guild_info_schema, tickets_schema = await to_thread(read_schemas)

        await self.db.executescript(logging_schema)
        await self.db.executescript(cases_schema)
        await self.db.executescript(partnerships_schema)
        await self.db.executescript(guild_info_schema)
        await self.db.executescript(tickets_schema)
        await self.db.commit()

        # ⸻ Guild Information

        data = await load_partnership_data(self.db)
        views, files = build_partnership_views(data["partnerships"])

        await ensure_views(
            bot        = self,
            channel_id = HIERARCHY_CHANNEL_ID,
            views      = HierarchyViewsList,
        )

        await ensure_views(
            bot        = self,
            channel_id = TICKETS_CHANNEL_ID,
            views      = [TicketComponents()],
        )
        self.add_view(TicketComponents())

        await ensure_views(
            bot        = self,
            channel_id = PARTNERSHIPS_CHANNEL_ID,
            views      = views,
            files      = files,
        )

        await ensure_views(
            bot        = self,
            channel_id = RULES_CHANNEL_ID,
            views      = RuleViewsList,
        )

        await ensure_views(
            bot        = self,
            channel_id = PARTNERSHIP_REQUIREMENTS_CHANNEL_ID,
            views      = PartnershipViewsList,
        )

        # ⸻ Cogs

        cogs  : list[str] = await to_thread(
            discover_cogs,
            "commands",
            "events",
            "core",
        )

        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info("Loaded cog %s", cog)
            except Exception:
                log.exception("Failed to load cog %s", cog)

    @override
    async def close(self) -> None:
        if hasattr(self, "db"):
            await self.db.close()

        await super().close()


bot  = Cordex()
tree = bot.tree
