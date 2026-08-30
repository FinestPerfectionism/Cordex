from typing import TYPE_CHECKING, final

from discord.app_commands import Choice, choices, command, describe, guild_only
from discord.ext import commands

from core.help import Argument, ArgumentType, help_description

from .info import Scope, run_member_info

if TYPE_CHECKING:
    from discord import Member

    from bot import Cordex, Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Member Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
@guild_only
class MemberCommands(
    commands.GroupCog,
    name        = "member",
    description = "Member commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /member info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(
        arguments = {
            "scope" : Argument(
                name        = "scope",
                type        = ArgumentType(
                    type     = "Choice",
                    choices  = ["Guild", "Global"],
                    optional = True,
                ),
                description = 'Whether to view the guild profile or the global profile of the member. Defaults to "global".',
            ),
        },
    )
    @command(
        name        = "info",
        description = "View information for a member.",
    )
    @describe(
        member = "The user to view information for. Defaults to yourself.",
        scope  = 'Whether to view the guild profile or the global profile of the member. Defaults to "global".',
    )
    @choices(
        scope = [
            Choice(
                name  = "Guild",
                value = "guild",
            ),
            Choice(
                name  = "Global",
                value = "global",
            ),
        ],
    )
    async def cmd_member_info(
        self,
        interaction : Interaction,
        member      : Member | None = None,
        *,
        scope       : Scope  | None = "global",
    ) -> None:
        await run_member_info(interaction, member, scope)

async def setup(bot : Cordex) -> None:
    cog = MemberCommands(bot)
    await bot.add_cog(cog)
