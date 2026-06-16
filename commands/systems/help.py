import discord
from discord.ext import commands
from discord.ui import (
    Container,
    LayoutView,
    TextDisplay,
)

from bot import Context, Cordex
from constants import BOT_OWNER_ID, COLOR_BLURPLE
from core.help import run_help

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

BOT_INFO_TEXT = (
     "# Bot Information\n"
     "Various moderative, administrative, and directive utilities for the staff team. "
     "This bot is unusable outside of The Goobers guild. Do __not__ expect to receive support with usage.\n"
     "## Modules\n"
     "- **Moderation** — Warnings, mutes, bans, and other punitive actions.\n"
     "- **Utility** — General-purpose staff tools.\n"
     "- **Proposal Manager** — Create and manage proposals.\n"
     "- **Applications & Tickets Manager** — Handle applications and support tickets.\n"
     "## Developer\n"
    f"<:developer:1480043201581551676> My developer is this bitch: <@{BOT_OWNER_ID}>\n"
     "## Usage\n"
     "Run `.help <cmd>` for detailed information on a specific command."
)

class InfoView(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(content = BOT_INFO_TEXT),
        accent_color = COLOR_BLURPLE,
    )

class HelpCommands(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot : Cordex = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .help Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "help")
    async def cmd_help(self, ctx : Context, *, command_name : str | None = None) -> None:
        if not command_name:
            _ = await ctx.send(
                view             = InfoView(),
                allowed_mentions = discord.AllowedMentions.none(),
            )
            return

        query = command_name.lower().strip()

        special_responses : dict[str, str] = {
            "cmd"                  : "Your stupidity is unfathomable.",
            "<cmd>"                : "Your stupidity is unfathomable.",
            "super_secret_command" : "There is no super secret command in ba sing se.",
            "help"                 : "Help²",
            "me"                   : "I'm a machine, not your fucking therapist.",
        }

        if query in special_responses:
            _ = await ctx.send(special_responses[query])
            return

        await run_help(self.bot, ctx, command_name)

async def setup(bot : Cordex) -> None:
    cog = HelpCommands(bot)
    await bot.add_cog(cog)
