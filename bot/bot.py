from asyncio import to_thread
from logging import Logger, getLogger
from pathlib import Path
from typing import TypedDict, Unpack, override

import aiosqlite as asq
from discord import CustomActivity, Intents, Message, Status
from discord import Interaction as BaseInteraction
from discord.ext import commands
from discord.ext.commands import (  # type: ignore[reportMissingTypeStubs]
    Context as BaseContext,
)
from discord.ext.commands.view import StringView  # type: ignore[reportMissingTypeStubs]

from core.cog_loader import discover_cogs

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


type Context     = ContextClass
type Interaction = BaseInteraction["Cordex"] | BaseInteraction

type ContextOrInteraction = Interaction | Context

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
        self.logging_db : asq.Connection

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

        self.logging_db = await asq.connect("database.db")

        def read_schema() -> str:
            with Path("schemas/logging.sql").open() as f:
                return f.read()

        schema : str = await to_thread(read_schema)

        await self.logging_db.executescript(schema)

        # ⸻ Cogs

        priority_load : list[str] = ["core.startup"]
        cogs          : list[str] = await to_thread(
            discover_cogs,
            "commands",
            "events",
            "core",
            priority = priority_load,
        )

        for cog in cogs:
            try:
                await self.load_extension(cog)
                log.info("Loaded cog %s", cog)
            except Exception:
                log.exception("Failed to load cog %s", cog)

    @override
    async def close(self) -> None:
        await self.logging_db.close()
        await super().close()


bot  = Cordex()
tree = bot.tree
