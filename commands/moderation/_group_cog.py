from discord.app_commands import Group, command, guild_only
from discord.ext import commands

from bot import Cordex, Interaction
from core.permissions import (
    director_cmd,
    moderator_cmd,
    senior_moderator_cmd,
    staff_cmd,
)

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
from .tickets import run_mod_tickets_close, run_mod_tickets_open

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@guild_only
class ModerationCommands(
    commands.GroupCog,
    name        = "moderation",
    description = "Moderators only — Moderation commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    lockdown   : Group = Group(
        name        = "lockdown",
        description = "Moderation lockdown commands",
    )
    ban        : Group = Group(
        name        = "ban",
        description = "Moderation ban commands",
    )
    quarantine : Group = Group(
        name        = "quarantine",
        description = "Moderation quarantine commands",
    )
    timeout    : Group = Group(
        name        = "timeout",
        description = "Moderation timeout commands",
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
    @senior_moderator_cmd()
    async def cmd_lockdown_add(self, interaction : Interaction) -> None:
        await run_mod_primary_lockdown_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation lockdown remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @lockdown.command(
        name        = "remove",
        description = "Remove channel(s) or the server from lockdown.",
    )
    @director_cmd()
    async def cmd_lockdown_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_lockdown_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation ban add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @ban.command(
        name        = "add",
        description = "Ban member(s) from the server.",
    )
    @senior_moderator_cmd()
    async def cmd_ban_add(self, interaction : Interaction) -> None:
        await run_mod_primary_ban_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation ban view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @ban.command(
        name        = "view",
        description = "View all banned members.",
    )
    @staff_cmd()
    async def cmd_ban_view(self, interaction : Interaction) -> None:
        await run_mod_primary_ban_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation ban remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @ban.command(
        name        = "remove",
        description = "Remove ban from member(s).",
    )
    @director_cmd()
    async def cmd_ban_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_ban_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation kick Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "kick",
        description = "Kick member(s) from the server.",
    )
    @senior_moderator_cmd()
    async def cmd_kick(self, interaction : Interaction) -> None:
        await run_mod_primary_kick(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "add",
        description = "Add member(s) to quarantine.",
    )
    @senior_moderator_cmd()
    async def cmd_quarantine_add(self, interaction : Interaction) -> None:
        await run_mod_primary_quarantine_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "view",
        description = "View all quarantined members.",
    )
    @staff_cmd()
    async def cmd_quarantine_view(self, interaction : Interaction) -> None:
        await run_mod_primary_quarantine_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation quarantine remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @quarantine.command(
        name        = "remove",
        description = "Remove member(s) from quarantine.",
    )
    @senior_moderator_cmd()
    async def cmd_quarantine_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_quarantine_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout add Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "add",
        description = "Add member(s) to timeout.",
    )
    @moderator_cmd()
    async def cmd_timeout_add(self, interaction : Interaction) -> None:
        await run_mod_primary_timeout_add(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout view Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "view",
        description = "View all timed out members.",
    )
    @staff_cmd()
    async def cmd_timeout_view(self, interaction : Interaction) -> None:
        await run_mod_primary_timeout_view(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation timeout remove Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @timeout.command(
        name        = "remove",
        description = "Remove member(s) from timeout.",
    )
    @senior_moderator_cmd()
    async def cmd_timeout_remove(self, interaction : Interaction) -> None:
        await run_mod_primary_timeout_remove(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation purge Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "purge",
        description = "Purge messages from member(s) or channel(s).",
    )
    @senior_moderator_cmd()
    async def cmd_purge(self, interaction : Interaction) -> None:
        await run_mod_primary_purge(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation tickets open Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @tickets.command(name = "open")
    @moderator_cmd()
    async def cmd_open(self, interaction : Interaction) -> None:
        await run_mod_tickets_open(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /moderation tickets close Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @tickets.command(name = "close")
    @moderator_cmd()
    async def cmd_close(self, interaction : Interaction) -> None:
        await run_mod_tickets_close(interaction)

async def setup(bot : Cordex) -> None:
    cog = ModerationCommands(bot)
    await bot.add_cog(cog)
