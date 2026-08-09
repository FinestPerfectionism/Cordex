from typing import final

from discord import Attachment, User
from discord.app_commands import (
    Choice,
    autocomplete,
    command,
    describe,
    guild_only,
    rename,
)
from discord.ext import commands

from bot import Cordex, Interaction
from core.help import HelpArgument, help_description
from core.permissions import director_cmd
from core.state import load_partnership_data

from .add import run_partnership_add
from .remove import run_partnership_remove
from .update import run_partnership_update

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Partnership Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
class PartnershipCommands(
    commands.GroupCog,
    name        = "partnership",
    description = "Directors only — Partnership commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Server Name Autocomplete
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def _server_name_autocomplete(self, _interaction : Interaction, current : str) -> list[Choice[str]]:
        data = await load_partnership_data(self.bot.db)
        return [
            Choice(name = p["server_name"], value = p["server_name"])
            for p in data["partnerships"] if current.lower() in p["server_name"].lower()
        ][:25]

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /partnership add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "server_picture": HelpArgument(
                name        = "server-picture",
                description = "The server's picture.",
            ),
            "server_name": HelpArgument(
                name        = "server-name",
                description = "The server's name.",
            ),
            "server_description": HelpArgument(
                name        = "server-description",
                description = "The server's description.",
            ),
            "server_owner": HelpArgument(
                name        = "server-owner",
                description = "The server's owner.",
            ),
            "server_link": HelpArgument(
                name        = "server-link",
                description = "The server's invite link. Must be a valid Discord invite of the form `https://discord.gg/example`.",
            ),
        },
    )
    @command(
        name        = "add",
        description = "Add a server partnership.",
    )
    @describe(
        server_picture     = "The server's picture.",
        server_name        = "The server's name.",
        server_description = "The server's description.",
        server_owner       = "The server's owner.",
        server_link        = "The server's invite link. Must be a valid Discord invite of the form \"https://discord.gg/example\".",
    )
    @director_cmd()
    @rename(
        server_picture     = "server-picture",
        server_name        = "server-name",
        server_description = "server-description",
        server_owner       = "server-owner",
        server_link        = "server-link",
    )
    async def cmd_partnership_add(
        self,
        interaction        : Interaction,
        server_picture     : Attachment,
        server_name        : str,
        server_description : str,
        server_owner       : User,
        server_link        : str,
    ) -> None:
        await run_partnership_add(
            self.bot,
            interaction,
            server_name,
            server_picture,
            server_description,
            server_owner,
            server_link,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /partnership update
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "server_name"        : HelpArgument(
                name        = "server-name",
                description = "The name of the server to update.",
            ),
            "server_picture"     : HelpArgument(
                name        = "server-picture",
                description = "The server's new picture.",
            ),
            "new_server_name"    : HelpArgument(
                name        = "new-server-name",
                description = "The server's new name.",
            ),
            "server_description" : HelpArgument(
                name        = "server-description",
                description = "The server's new description.",
            ),
            "server_owner"       : HelpArgument(
                name        = "server-owner",
                description = "The server's new owner.",
            ),
            "server_link"        : HelpArgument(
                name        = "server-link",
                description = "The server's new invite link. Must be a valid Discord invite of the form `https://discord.gg/example`.",
            ),
        },
    )
    @command(
        name        = "update",
        description = "Update an existing server partnership.",
    )
    @describe(
        server_name        = "The name of the server to update.",
        server_picture     = "The server's new picture.",
        new_server_name    = "The server's new name.",
        server_description = "The server's new description.",
        server_owner       = "The server's new owner.",
        server_link        = "The server's new invite link. Must be a valid Discord invite of the form \"https://discord.gg/example\".",
    )
    @rename(
        server_name        = "server-name",
        server_picture     = "server-picture",
        new_server_name    = "new-server-name",
        server_description = "server-description",
        server_owner       = "server-owner",
        server_link        = "server-link",
    )
    @autocomplete(server_name = _server_name_autocomplete)
    @director_cmd()
    async def cmd_partnership_update(
        self,
        interaction        : Interaction,
        server_name        : str,
        server_picture     : Attachment | None = None,
        new_server_name    : str        | None = None,
        server_description : str        | None = None,
        server_owner       : User       | None = None,
        server_link        : str        | None = None,
    ) -> None:
        await run_partnership_update(
            self.bot,
            interaction,
            server_name,
            server_picture,
            new_server_name,
            server_description,
            server_owner,
            server_link,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /partnership remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "server_name" : HelpArgument(
                name        = "server-name",
                description = "The name of the server to remove.",
            ),
        },
    )
    @command(
        name        = "remove",
        description = "Remove a server partnership.",
    )
    @describe(server_name = "The name of the server to remove.")
    @rename(server_name = "server-name")
    @autocomplete(server_name = _server_name_autocomplete)
    @director_cmd()
    async def cmd_partnership_remove(
        self,
        interaction : Interaction,
        server_name : str,
    ) -> None:
        await run_partnership_remove(
            self.bot,
            interaction,
            server_name,
        )

async def setup(bot : Cordex) -> None:
    cog = PartnershipCommands(bot)
    await bot.add_cog(cog)
