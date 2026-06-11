import asyncio
import logging
from pathlib import Path

import aiosqlite as asq
import discord
from discord import CustomActivity, Intents, Status
from discord.ext import commands
from typing_extensions import override

from core.cog_loader import discover_cogs

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot & Client Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

log : logging.Logger = logging.getLogger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cordex Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class Cordex(commands.Bot):
    def __init__(self) -> None:
        intents : Intents = Intents.all()
        super().__init__(
            command_prefix   = commands.when_mentioned_or("."),
            intents          = intents,
            case_insensitive = True,
            help_command     = None,
            status           = Status.online,
            activity         = CustomActivity(name = "Utility Bot 2.0!"),
        )
        self.cases_db   : asq.Connection
        self.start_time : float

    @override
    async def setup_hook(self) -> None:

        # ⸻ Aiosqlite

        # self.cases_db = await asq.connect("data/cases.db")
        # def read_schema() -> str:
        #     with Path("schemas/cases.sql").open() as file:
        #         return file.read()

        # schema_sql = await asyncio.to_thread(read_schema)
        # _ = await self.cases_db.executescript(schema_sql)
        # try:
        #     await self.cases_db.commit()
        # except asq.OperationalError:
        #     log.exception("Unable to open database file")

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

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Context and Interaction Classes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type Context     = commands.Context[Cordex]
type Interaction = discord.Interaction[Cordex] | discord.Interaction

CtxOrInteraction = Context | Interaction
