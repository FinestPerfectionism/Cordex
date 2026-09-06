from typing import final, override

from discord import Member
from discord.app_commands import (
    AppCommandError,
    BotMissingPermissions,
    Group,
    Range,
    command,
    describe,
    guild_only,
)
from discord.app_commands.checks import bot_has_permissions
from discord.ext import commands

from bot import Cordex, Interaction
from core.exceptions import send_bad_request
from core.permissions import bot_owner_cmd
from core.utilities import unimplemented

from .cases import run_mod_cases_query, run_mod_cases_view
from .primary._base import UnconfiguredQuarantine, quarantine_cmd
from .primary.ban import (
    run_mod_primary_ban_add,
    run_mod_primary_ban_remove,
    run_mod_primary_ban_view,
)
from .primary.kick import run_mod_primary_kick
from .primary.lockdown import (
    run_mod_primary_lockdown_add,
    run_mod_primary_lockdown_remove,
)
from .primary.note import (
    run_mod_primary_note_add,
    run_mod_primary_note_remove,
    run_mod_primary_note_view,
)
from .primary.purge import run_mod_primary_purge
from .primary.quarantine import (
    run_mod_primary_quarantine_add,
    run_mod_primary_quarantine_remove,
    run_mod_primary_quarantine_view,
)
from .primary.timeout import (
    run_mod_primary_timeout_add,
    run_mod_primary_timeout_remove,
    run_mod_primary_timeout_view,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
class ModerationCommands(
    commands.GroupCog,
    name        = "moderation",
    description = "Moderators only — Moderation commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    ban        : Group = Group(
        name        = "ban",
        description = "Moderation ban commands",
    )
    lockdown   : Group = Group(
        name        = "lockdown",
        description = "Moderation lockdown commands",
    )
    note       : Group = Group(
        name        = "note",
        description = "Moderation note commands",
    )
    quarantine : Group = Group(
        name        = "quarantine",
        description = "Moderation quarantine commands",
    )
    timeout    : Group = Group(
        name        = "timeout",
        description = "Moderation timeout commands",
    )
    cases      : Group = Group(
        name        = "cases",
        description = "Moderation case commands",
    )

    @override
    async def cog_app_command_error(self, interaction : Interaction, error : AppCommandError) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        if isinstance(error, UnconfiguredQuarantine):
            await send_bad_request(
                interaction,
                subtitle = "This server has not configured a quarantine role, so quarantine operations cannot be performed",
            )

        if isinstance(error, BotMissingPermissions):
            await send_bad_request(
                interaction,
                subtitle = "This command requires certain permissions to run that I lack",
            )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation lockdown add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @lockdown.command(
        name        = "add",
        description = "Add channel(s) or the server to lockdown.",
    )
    @bot_has_permissions(manage_channels = True)
    @bot_owner_cmd()
    async def cmd_mod_primary_lockdown_add(self, interaction : Interaction) -> None:
        await run_mod_primary_lockdown_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation lockdown remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @lockdown.command(
        name        = "remove",
        description = "Remove channel(s) or the server from lockdown.",
    )
    @bot_has_permissions(manage_channels = True)
    @bot_owner_cmd()
    async def cmd_mod_primary_lockdown_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_lockdown_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation ban add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @ban.command(
        name        = "add",
        description = "Ban member(s) from the server.",
    )
    @bot_has_permissions(ban_members = True)
    @describe(target = "The member to ban.")
    @bot_owner_cmd()
    async def cmd_mod_primary_ban_add(self, interaction : Interaction, target : Member) -> None:
        await run_mod_primary_ban_add(interaction, target)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation ban view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @ban.command(
        name        = "view",
        description = "View all banned members.",
    )
    @bot_owner_cmd()
    async def cmd_mod_primary_ban_view(self, interaction : Interaction) -> None:
        await run_mod_primary_ban_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation ban remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @ban.command(
        name        = "remove",
        description = "Remove a ban from member(s).",
    )
    @bot_has_permissions(ban_members = True)
    @describe(target = "The ID of the member to unban. Must be between 17-19.")
    @bot_owner_cmd()
    async def cmd_mod_primary_ban_remove(self, interaction : Interaction, target : Range[str, 17, 19]) -> None:
        await run_mod_primary_ban_remove(interaction, target)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation kick Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "kick",
        description = "Kick member(s) from the server.",
    )
    @bot_has_permissions(kick_members = True)
    @describe(target = "The member to kick.")
    @bot_owner_cmd()
    async def cmd_mod_primary_kick(self, interaction : Interaction, target : Member) -> None:
        await run_mod_primary_kick(interaction, target)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "add",
        description = "Add member(s) to quarantine.",
    )
    @bot_has_permissions(manage_roles = True)
    @describe(target = "The member to place in quarantine.")
    @quarantine_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_quarantine_add(self, interaction : Interaction, target : Member) -> None:
        await run_mod_primary_quarantine_add(interaction, target)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "view",
        description = "View all quarantined members.",
    )
    @quarantine_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_quarantine_view(self, interaction : Interaction) -> None:
        await run_mod_primary_quarantine_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "remove",
        description = "Remove member(s) from quarantine.",
    )
    @bot_has_permissions(manage_roles = True)
    @describe(target = "The member to remove from quarantine.")
    @quarantine_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_quarantine_remove(self, interaction : Interaction, target : Member) -> None:
        await run_mod_primary_quarantine_remove(interaction, target)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "add",
        description = "Add member(s) to timeout.",
    )
    @bot_has_permissions(moderate_members = True)
    @describe(target = "The member to place in timeout.")
    @bot_owner_cmd()
    async def cmd_mod_primary_timeout_add(self, interaction : Interaction, target : Member) -> None:
        await run_mod_primary_timeout_add(interaction, target)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "view",
        description = "View all timed out members.",
    )
    @bot_owner_cmd()
    async def cmd_mod_primary_timeout_view(self, interaction : Interaction) -> None:
        await run_mod_primary_timeout_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "remove",
        description = "Remove member(s) from timeout.",
    )
    @bot_has_permissions(moderate_members = True)
    @describe(target = "The member to remove from timeout.")
    @bot_owner_cmd()
    async def cmd_mod_primary_timeout_remove(self, interaction : Interaction, target : Member) -> None:
        await run_mod_primary_timeout_remove(interaction, target)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation purge Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "purge",
        description = "Purge messages from member(s) or channel(s).",
    )
    @bot_has_permissions(manage_messages = True, read_message_history = True)
    @bot_owner_cmd()
    async def cmd_mod_primary_purge(self, interaction : Interaction) -> None:
        await run_mod_primary_purge(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation note add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @note.command(
        name        = "add",
        description = "Add a note to a member.",
    )
    @bot_owner_cmd()
    async def cmd_mod_primary_note_add(self, interaction : Interaction) -> None:
        await run_mod_primary_note_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation note view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @note.command(
        name        = "view",
        description = "View a member's notes.",
    )
    @bot_owner_cmd()
    async def cmd_mod_primary_note_view(self, interaction : Interaction) -> None:
        await run_mod_primary_note_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation note remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @note.command(
        name        = "remove",
        description = "Remove a note from a member.",
    )
    @bot_owner_cmd()
    async def cmd_mod_primary_note_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_note_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation cases query Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cases.command(
        name        = "query",
        description = "Query moderation cases with various filters.",
    )
    @unimplemented()
    async def cmd_mod_cases_query(self, interaction : Interaction) -> None:
        await run_mod_cases_query(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation cases view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cases.command(
        name        = "view",
        description = "View a moderation case by it's ID.",
    )
    @unimplemented()
    async def cmd_mod_cases_view(self, interaction : Interaction) -> None:
        await run_mod_cases_view(interaction)

# async def setup(bot : Cordex) -> None:
#     cog = ModerationCommands(bot)
#     await bot.add_cog(cog)
