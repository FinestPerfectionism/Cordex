from typing import final

from discord.app_commands import Group, command, guild_only
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import (
    bot_owner_cmd,
    # director_cmd,
    moderator_cmd,
)

# senior_moderator_cmd,
# staff_cmd,
from core.utilities import unimplemented

from .cases import run_mod_cases_query, run_mod_cases_view
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
from .tickets import (
    run_mod_tickets_close,
    run_mod_tickets_escalate,
    run_mod_tickets_open,
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
    tickets    : Group = Group(
        name        = "tickets",
        description = "Moderation ticket commands",
    )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation lockdown add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @lockdown.command(
        name        = "add",
        description = "Add channel(s) or the server to lockdown.",
    )
    # @senior_moderator_cmd()
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
    # @director_cmd()
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
    # @senior_moderator_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_ban_add(self, interaction : Interaction) -> None:
        await run_mod_primary_ban_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation ban view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @ban.command(
        name        = "view",
        description = "View all banned members.",
    )
    # @staff_cmd()
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
    # @director_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_ban_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_ban_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation kick Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "kick",
        description = "Kick member(s) from the server.",
    )
    # @senior_moderator_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_kick(self, interaction : Interaction) -> None:
        await run_mod_primary_kick(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "add",
        description = "Add member(s) to quarantine.",
    )
    # @senior_moderator_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_quarantine_add(self, interaction : Interaction) -> None:
        await run_mod_primary_quarantine_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "view",
        description = "View all quarantined members.",
    )
    # @staff_cmd()
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
    # @senior_moderator_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_quarantine_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_quarantine_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "add",
        description = "Add member(s) to timeout.",
    )
    # @moderator_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_timeout_add(self, interaction : Interaction) -> None:
        await run_mod_primary_timeout_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "view",
        description = "View all timed out members.",
    )
    # @staff_cmd()
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
    # @senior_moderator_cmd()
    @bot_owner_cmd()
    async def cmd_mod_primary_timeout_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_timeout_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation purge Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "purge",
        description = "Purge messages from member(s) or channel(s).",
    )
    # @senior_moderator_cmd()
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
    # @moderator_cmd()
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
    # @staff_cmd()
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
    # @moderator_cmd()
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
    # @moderator_cmd()
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
    # @moderator_cmd()
    @unimplemented()
    async def cmd_mod_cases_view(self, interaction : Interaction) -> None:
        await run_mod_cases_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation tickets open Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @tickets.command(
        name        = "open",
        description = "Open a ticket thread.",
    )
    @moderator_cmd()
    async def cmd_mod_tickets_open(self, interaction : Interaction) -> None:
        await run_mod_tickets_open(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation tickets escalate Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @tickets.command(
        name        = "escalate",
        description = "Escalate a ticket thread.",
    )
    @moderator_cmd()
    async def cmd_mod_tickets_escalate(self, interaction : Interaction) -> None:
        await run_mod_tickets_escalate(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation tickets close Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @tickets.command(
        name        = "close",
        description = "Close a ticket thread.",
    )
    @moderator_cmd()
    async def cmd_mod_tickets_close(self, interaction : Interaction) -> None:
        await run_mod_tickets_close(interaction)

# async def setup(bot : Cordex) -> None:
#     cog = ModerationCommands(bot)
#     await bot.add_cog(cog)
