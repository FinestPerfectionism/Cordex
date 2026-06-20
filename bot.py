from logging import Logger, getLogger
from typing import TYPE_CHECKING, Self, TypedDict, Unpack, override

from discord import CustomActivity, Intents, Message, Status
from discord import Interaction as BaseInteraction
from discord.ext import commands
from discord.ext.commands import (  # type: ignore[reportMissingTypeStubs]
    Context as BaseContext,
)
from discord.ext.commands.view import StringView  # type: ignore[reportMissingTypeStubs]
from discord.ui import LayoutView, View

from core.cog_loader import discover_cogs

if TYPE_CHECKING:
    import aiosqlite as asq

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot & Client Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

log : Logger = getLogger("Cordex")

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

    async def send_view(self, ctx : Self, view : View | LayoutView) -> None:
        _ = await ctx.send(view = view)


type Context          = ContextClass
type Interaction      = BaseInteraction["Cordex"] | BaseInteraction
type CtxOrInteraction = Interaction | Context

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cordex Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Cordex(commands.Bot):
    def __init__(self) -> None:
        intents : Intents = Intents.all()
        super().__init__(
            command_prefix   = commands.when_mentioned_or("c!", "c.", "C!", "C."),
            intents          = intents,
            case_insensitive = True,
            help_command     = None,
            status           = Status.online,
            activity         = CustomActivity(name = "Utility Bot 1.5."),
        )
        self.cases_db   : asq.Connection
        self.start_time : float

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

        # ⸻ Cogs

        priority_load : list[str] = ["core.startup"]
        cogs          : list[str] = discover_cogs(
            "commands",
            "events",
            "core",
            priority = priority_load,
        )

        for cog  in cogs:
            try:
                await self.load_extension(cog)
                log.info("Loaded cog %s", cog)
            except Exception:
                log.exception("Failed to load cog %s", cog)

    @override
    async def close(self) -> None:
        if hasattr(self, "cases_db"):
            await self.cases_db.close()
            log.info("Cases database connection closed successfully")

        await super().close()


bot  = Cordex()
tree = bot.tree
