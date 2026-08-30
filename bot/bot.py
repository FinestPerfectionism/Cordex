from asyncio import to_thread
from collections.abc import Awaitable, Callable
from logging import getLogger as get_logger
from pathlib import Path
from typing import Self, TypedDict, Unpack, cast, final, override

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
from core.state import Connection, connect

from .types import NameStyleResult
from .ui import Button, LayoutView, Modal, View, button

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot & Client Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


log = get_logger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Context and Interaction Classes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type _Inter = Callable[[Interaction], Awaitable[None]]

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
type Interaction          = BaseInteraction[Cordex]
type ContextOrInteraction = Interaction | Context

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cordex Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class Cordex(commands.Bot):
    def __init__(self) -> None:
        prefix  = commands.when_mentioned_or(".")
        intents = Intents.all()
        status  = Status.online

        super().__init__(
            command_prefix = prefix,
            intents        = intents,
            help_command   = None,
            status         = status,
        )
        self.db : Connection

        self._commands_cache     : list[Command[Group | Cog, ..., object] | Group] = []
        self._app_commands_cache : list[AppCommand] = []

        self.restarting : bool = False

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Name Styles
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_name_style(
        self,
        *,
        guild     : Guild,
        font_id   : DisplayNameFont,
        effect_id : DisplayNameEffect,
        colors    : list[str],
    ) -> None:
        color_integers = [int(hex_code, 16) for hex_code in colors]

        await self.http.request(
            route = Route("PATCH", "/guilds/{guild_id}/members/@me", guild_id = guild.id),
            json  = {
              "display_name_font_id"   : font_id.value,
              "display_name_effect_id" : effect_id.value,
              "display_name_colors"    : color_integers,
            },
        )

    async def get_name_style(self, guild : Guild, /) -> NameStyleResult:
        class NameStylePayload(TypedDict):
            font_id   : int
            effect_id : int
            colors    : list[int]

        class MemberNameStylePayload(TypedDict):
            display_name_styles : NameStylePayload

        # ⸻ It's very unlikely that self.user is None, but pyright will complain anyway.

        if self.user is None:
            error = "Client user is not logged in."
            raise ValueError(error)

        response = cast(
            MemberNameStylePayload,
            await self.http.request(
                route = Route(
                    "GET", "/guilds/{guild_id}/members/{user_id}",
                    guild_id = guild.id,
                    user_id  = self.user.id,
                ),
            ),
        )

        styles = response["display_name_styles"]

        return NameStyleResult(
            font_id   = DisplayNameFont(styles["font_id"]),
            effect_id = DisplayNameEffect(styles["effect_id"]),
            colors    = [f"{color:06x}" for color in styles["colors"]],
        )

    async def reset_name_style(self, *, guild : Guild, branded : bool = True) -> None:

        # ⸻ Branded is the bot's special scheme instead of a normal discord font.

        await self.set_name_style(
            guild     = guild,
            font_id   = DisplayNameFont.zilla_slab if branded else DisplayNameFont.default,
            effect_id = DisplayNameEffect.gradient if branded else DisplayNameEffect.solid,
            colors    = ["FFFFFF", "000000"]       if branded else ["FFFFFF", "FFFFFF"],
        )

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

        def read_schemas() -> tuple[str, str]:
            with Path("schemas/logging.sql").open(encoding = "utf-8") as f1:
                logging_sql = f1.read()
            with Path("schemas/cases.sql").open(encoding = "utf-8") as f2:
                cases_sql = f2.read()
            return logging_sql, cases_sql

        logging_schema, cases_schema = await to_thread(read_schemas)

        for schema in [logging_schema, cases_schema]:
            await self.db.executescript(schema)

        await self.db.commit()

        # ⸻ Cogs

        cogs = await to_thread(
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
        if self.db:
            await self.db.close()

        await super().close()


bot  = Cordex()
tree = bot.tree
