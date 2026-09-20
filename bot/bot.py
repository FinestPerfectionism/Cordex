# pyright: reportImportCycles = false

# ⸻ It's going to complain about 'Interaction'.

from asyncio import to_thread
from contextlib import suppress
from inspect import getsource
from io import BytesIO
from logging import getLogger as get_logger
from pathlib import Path
from types import (
    CodeType,
    FrameType,
    FunctionType,
    MethodType,
    ModuleType,
    TracebackType,
)
from typing import Self, TypedDict, Unpack, cast, final, override

from discord import Embed, File, Guild, Intents, Member, Message, Status, User
from discord import Interaction as BaseInteraction
from discord.app_commands import AppCommand, Command, CommandTree
from discord.ext import commands
from discord.ext.commands import (  # pyright: ignore[reportMissingTypeStubs]
    Context as BaseContext,
)
from discord.ext.commands.view import (  # pyright: ignore[reportMissingTypeStubs]
    StringView,
)
from discord.http import Route

from constants import DENIED_EMOJI, DEVELOPER_IDS, DisplayNameEffect, DisplayNameFont
from core.cog_loader import discover_cogs
from core.state import Config, Connection, Restriction, connect, is_restrictable

from .types import AnnotatedCommand, LambdaInter, NameStyleResult
from .ui import Button, LayoutView, Modal, View, button

InspectableObject = (
    ModuleType
    | type
    | MethodType
    | FunctionType
    | TracebackType
    | FrameType
    | CodeType
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot & Client Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


log = get_logger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Context and Interaction Classes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


class _ContextKwargs(TypedDict, total = False):
    message : Message
    bot     : Cordex
    view    : StringView


class _ContextClass(BaseContext["Cordex"]):
    def __init__(self, **kwargs : Unpack[_ContextKwargs]) -> None:
        super().__init__(**kwargs)

    async def send_button(self, callback : LambdaInter, /) -> Message:
        @final
        class _ViewButton(View):
            def __init__(self, view_callback : LambdaInter, /) -> None:
                super().__init__(timeout = None)
                self.callback = view_callback

            @button(label = "Click me!")
            async def btn_basic(self, interaction : Interaction, _button : Button[Self]) -> None:
                try:
                    await self.callback(interaction)
                except Exception as e:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                           f"{DENIED_EMOJI} **Error! :[**\n"
                            "```py\n"
                           f"{e}\n"
                            "```",
                            ephemeral = True,
                        )
                    else:
                        await interaction.followup.send(
                           f"{DENIED_EMOJI} **Error! :[**\n"
                            "```py\n"
                           f"{e}\n"
                            "```",
                            ephemeral = True,
                        )

        return await self.send(view = _ViewButton(callback))

    async def send_embed(self, embed : Embed, /) -> Message:
        return await self.send(embed = embed)

    async def send_view(self, view : View | LayoutView, /) -> Message:
        return await self.send(view = view)

    async def send_modal(self, modal : Modal, /) -> Message:
        async def func(interaction : Interaction) -> None:
            await interaction.response.send_modal(modal)

        return await self.send_button(func)

    async def show_attrs(
        self,
        target   : object,
        /,
        *,
        tall     : bool | None = None,
        dunders  : bool        = False,
        privates : bool        = False,
    ) -> Message:
        def _filter(attr : str) -> bool:
            if attr.startswith("__") and attr.endswith("__"):
                return dunders
            if attr.startswith("_"):
                return privates
            return True

        attrs = [attr for attr in dir(target) if _filter(attr)]

        if tall is None:
            estimated_length = sum(len(a) for a in attrs) + (2 * (len(attrs) - 1))
            tall = estimated_length > 80

        joiner = ",\n" if tall else ", "

        return await self.send(
            "```py"
           f"{joiner.join(attrs)}"
            "```",
        )

    async def show_def(self, target : InspectableObject, /) -> Message:
        source = getsource(target)
        msg    = (
            "```py\n"
           f"{source}\n"
            "```"
        )

        if len(msg) < 2000:
            return await self.send(msg)

        module   = getattr(target, "__module__", "global").replace(".", "/")
        qualname = getattr(target, "__qualname__", "object").replace(".", "/")
        filename = f"{module}/{qualname}.py"
        return await self.send(file = File(BytesIO(source.encode()), filename = filename))

    async def reference_delete(self) -> None:
        if self.message.reference and self.message.reference.message_id:
            with suppress(Exception):
                reference_message = await self.channel.fetch_message(self.message.reference.message_id)
                await reference_message.delete()


class _Tree(CommandTree):
    @override
    async def interaction_check(self, interaction : Interaction) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        command = interaction.command
        guild   = interaction.guild
        user    = interaction.user

        if not isinstance(command, Command) or guild is None or not isinstance(user, Member):
            return True

        if not is_restrictable(command):
            return True

        restriction = interaction.client.get_restriction(guild.id, command.qualified_name)
        if restriction is None:
            return True

        if user.id == guild.owner_id or user.id in DEVELOPER_IDS or restriction.allows(user):
            return True

        await interaction.response.send_message(
           f"{DENIED_EMOJI} **Failed to run command!**\n"
            "You are not authorized to run this command.\n"
            "-# Bad request.",
            ephemeral = True,
        )
        return False


type Context              = _ContextClass
type Interaction          = BaseInteraction[Cordex]
type ContextOrInteraction = Interaction | Context

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cordex Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class Cordex(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            chunk_guilds_at_startup = True,
            command_prefix          = commands.when_mentioned_or("."),
            help_command            = None,
            intents                 = Intents.all(),
            status                  = Status.online,
            tree_cls                = _Tree,
        )
        self.version : float = 1.0

        self.db : Connection

        self._commands_cache     : list[AnnotatedCommand]             = []
        self._api_commands_cache : list[AppCommand]                   = []
        self._restrictions_cache : dict[tuple[int, str], Restriction] = {}

        self.restarting : bool = False

        self.developers : list[User] = []

    @property
    def id(self) -> int | None:
        return self.user.id if self.user else None

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Configuration
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def config(self, guild : Guild) -> Config:
        return Config(self, guild)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Name Styles
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def set_name_style(
        self,
        guild     : Guild,
        /,
        *,
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

    async def get_name_style(self, guild : Guild, /) -> NameStyleResult | None:
        class NameStylePayload(TypedDict):
            font_id   : int
            effect_id : int
            colors    : list[int]

        class MemberNameStylePayload(TypedDict):
            display_name_styles : NameStylePayload

        # ⸻ It's very unlikely that self.user is None, but pyright will complain anyway.

        if self.user is None:
            return None

        response = cast(
            "MemberNameStylePayload",
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

    async def reset_name_style(self, guild : Guild, /, *, branded : bool = True) -> None:

        # ⸻ Branded is the bot's special scheme instead of a normal discord font.

        await self.set_name_style(
            guild,
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
        if self.user:
            log.info("Logging in as %s, %s", self.user.name, self.user.id)

        self.developers = [user for developer_id in DEVELOPER_IDS if (user := await self.fetch_user(developer_id))]

        # ⸻ AIOSQLite

        db_path = Path("data/database.db")
        db_path.parent.mkdir(parents = True, exist_ok = True)

        self.db = await connect(str(db_path))

        def read_schemas() -> tuple[str, ...]:
            config_sql       = Path("schemas/config.sql").read_text(encoding = "utf-8")
            cases_sql        = Path("schemas/cases.sql").read_text(encoding = "utf-8")
            quarantines_sql  = Path("schemas/quarantines.sql").read_text(encoding = "utf-8")
            notes_sql        = Path("schemas/notes.sql").read_text(encoding = "utf-8")
            restrictions_sql = Path("schemas/command_restrictions.sql").read_text(encoding = "utf-8")
            return config_sql, cases_sql, quarantines_sql, notes_sql, restrictions_sql

        for schema in await to_thread(read_schemas):
            await self.db.executescript(schema)

        await self.db.commit()

        # ⸻ Cogs

        cogs = await to_thread(
            discover_cogs,
            "commands",
            "systems",
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
        await self.build_api_commands_cache()
        await self.build_restrictions_cache()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Commands Cache
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def build_commands_cache(self) -> None:
        self._commands_cache = list(self.tree.walk_commands())

    async def build_api_commands_cache(self) -> None:
        self._api_commands_cache = await self.tree.fetch_commands()

    def get_commands_cache(self) -> list[AnnotatedCommand]:
        if not self._commands_cache:
            self.build_commands_cache()
        return self._commands_cache

    def get_api_commands_cache(self) -> list[AppCommand]:
        return self._api_commands_cache

    def rebuild_commands_cache(self) -> None:
        self._commands_cache.clear()
        self.build_commands_cache()

    async def rebuild_api_commands_cache(self) -> None:
        self._api_commands_cache.clear()
        await self.build_api_commands_cache()

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Restrictions Cache
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def build_restrictions_cache(self) -> None:
        grouped : dict[tuple[int, str], tuple[set[int], set[int]]] = {}

        async with self.db.execute(
            t"SELECT guild_id, command_name, target_type, target_id FROM CommandRestrictions",
        ) as cursor:
            rows = await cursor.fetchall()

        for row in rows:
            guild_id     = cast("int", row[0])
            command_name = cast("str", row[1])
            target_type  = cast("str", row[2])
            target_id    = cast("int", row[3])

            users, roles = grouped.setdefault((guild_id, command_name), (set(), set()))

            if target_type == "role":
                roles.add(target_id)
            else:
                users.add(target_id)

        self._restrictions_cache = {
            key : Restriction(frozenset(users), frozenset(roles))
            for key, (users, roles) in grouped.items()
        }

    def get_restriction(self, guild_id : int, command_name : str, /) -> Restriction | None:
        return self._restrictions_cache.get((guild_id, command_name))

    def set_restriction(self, guild_id : int, command_name : str, restriction : Restriction | None, /) -> None:
        key = (guild_id, command_name)

        if restriction is None:
            self._restrictions_cache.pop(key, None)
        else:
            self._restrictions_cache[key] = restriction

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # close
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @override
    async def close(self) -> None:
        if self.db:
            await self.db.close()

        await super().close()
