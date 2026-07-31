from asyncio import to_thread
from collections.abc import Callable, Coroutine
from logging import getLogger as get_logger
from pathlib import Path
from typing import Self, TypedDict, Unpack, final, override

from aiosqlite import Connection, connect
from discord import Embed, Guild, Intents, Message, Status
from discord import Interaction as BaseInteraction
from discord.app_commands import AppCommand, Command, Group
from discord.ext import commands
from discord.ext.commands import Cog  # type: ignore[reportMissingTypeStubs]
from discord.ext.commands import (  # type: ignore[reportMissingTypeStubs]
    Context as BaseContext,
)
from discord.ext.commands.view import StringView  # type: ignore[reportMissingTypeStubs]
from discord.http import Route

from constants import DENIED_EMOJI, DisplayNameEffect, DisplayNameFont
from core.cog_loader import discover_cogs

from .ui import Button, LayoutView, Modal, View, button

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot & Client Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

log = get_logger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Context and Interaction Classes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type _Inter = Callable[[Interaction], Coroutine[None, None, None]]

class _ContextKwargs(TypedDict, total = False):
    message : Message
    bot     : "Cordex"
    view    : StringView

class _ContextClass(BaseContext["Cordex"]):
    def __init__(self, **kwargs : Unpack[_ContextKwargs]) -> None:
        super().__init__(**kwargs)

    async def send_button(self, callback : _Inter, /) -> None:
        @final
        class _ViewButton(View):
            def __init__(self, view_callback : _Inter, /) -> None:
                super().__init__(timeout = None)
                self.callback = view_callback

            @button(label = "Click me!")
            async def btn_basic(self, interaction : "Interaction", _button : Button[Self]) -> None:
                try:
                    await self.callback(interaction)
                except Exception as e:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            (
                               f"{DENIED_EMOJI} **Error! :[**\n"
                                "```py\n"
                               f"{e}\n"
                                "```"
                            ),
                            ephemeral = True,
                        )
                    else:
                        await interaction.followup.send(
                            (
                               f"{DENIED_EMOJI} **Error! :[**\n"
                                "```py\n"
                               f"{e}\n"
                                "```"
                            ),
                            ephemeral = True,
                        )

        await self.send(view = _ViewButton(callback))

    async def send_embed(self, embed : Embed, /) -> None:
        await self.send(embed = embed)

    async def send_view(self, view : View | LayoutView, /) -> None:
        await self.send(view = view)

    async def send_modal(self, modal : Modal, /) -> None:
        async def func(interaction : Interaction) -> None:
            await interaction.response.send_modal(modal)

        await self.send_button(func)


type Context              = _ContextClass
type Interaction          = BaseInteraction[Cordex] | BaseInteraction
type ContextOrInteraction = Interaction | Context

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cordex Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class Cordex(commands.Bot):
    def __init__(self) -> None:
        prefix   = commands.when_mentioned_or(".")
        intents  = Intents.all()
        status   = Status.online

        super().__init__(
            command_prefix   = prefix,
            intents          = intents,
            case_insensitive = True,
            help_command     = None,
            status           = status,
        )
        self.db                  : Connection
        self._commands_cache     : list[Command[Group | Cog, ..., object] | Group] = []
        self._app_commands_cache : list[AppCommand] = []

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # set_name_style
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_name_style(
        self,
        *,
        guild     : Guild,
        font_id   : DisplayNameFont,
        effect_id : DisplayNameEffect,
        colors    : list[str],
    ) -> None:
        route = Route("PATCH", "/guilds/{guild_id}/members/@me", guild_id = guild.id)

        color_integers = [int(hex_code, 16) for hex_code in colors]

        payload = {
          "display_name_font_id"   : font_id,
          "display_name_effect_id" : effect_id,
          "display_name_colors"    : color_integers,
        }
        await self.http.request(route, json = payload)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Custom Context
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @override
    async def get_context[ContextT : BaseContext[Cordex]](
        self,
        origin : Message        | BaseInteraction,
        *,
        cls    : type[ContextT] | None = None,
    ) -> ContextT | Context:
        return await super().get_context(origin, cls = cls or _ContextClass)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # setup_hook
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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

        # ⸻ Cache

        self.build_commands_cache()
        await self.build_app_commands_cache()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Commands Cache
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def build_commands_cache(self) -> None:
        self._commands_cache = list(self.tree.walk_commands())

    async def build_app_commands_cache(self) -> None:
        self._app_commands_cache = await self.tree.fetch_commands()

    def get_commands_cache(self) -> list[Command[Group | Cog, ..., object] | Group]:
        if not self._commands_cache:
            self.build_commands_cache()
        return self._commands_cache

    def get_app_commands_cache(self) -> list[AppCommand]:
        return self._app_commands_cache

    async def rebuild_commands_cache(self) -> None:
        self._commands_cache.clear()
        self._app_commands_cache.clear()

        self.build_commands_cache()
        await self.build_app_commands_cache()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # close
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @override
    async def close(self) -> None:
        if hasattr(self, "db"):
            await self.db.close()

        await super().close()


bot  = Cordex()
tree = bot.tree
