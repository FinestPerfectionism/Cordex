from logging import Logger, getLogger
from typing import TYPE_CHECKING, override

import discord
from discord import CustomActivity, Intents, Status
from discord.ext import commands

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

class ContextClass(commands.Context["Cordex"]):
    ...


type Context          = ContextClass
type Interaction      = discord.Interaction["Cordex"] | discord.Interaction
type CtxOrInteraction = Interaction | Context

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cordex Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Cordex(commands.Bot):
    def __init__(self) -> None:
        intents : Intents = Intents.all()
        super().__init__(
            command_prefix   = commands.when_mentioned_or("c!"),
            intents          = intents,
            case_insensitive = True,
            help_command     = None,
            status           = Status.online,
            activity         = CustomActivity(name = "Utility Bot 1.5."),
        )
        self.cases_db   : asq.Connection
        self.start_time : float

    @override
    async def get_context[ContextT : commands.Context[Cordex]](
        self,
        origin : discord.Message | discord.Interaction,
        *,
        cls    : type[ContextT]  | None = None,
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
