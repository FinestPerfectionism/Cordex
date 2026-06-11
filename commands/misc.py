import platform
import time

import discord
import psutil
from discord import app_commands
from discord.ext import commands

from bot import Context, Cordex, Interaction
from constants import (
    ACCEPTED_EMOJI,
    BOT_OWNER_ID,
    CONTESTED_EMOJI,
    DENIED_EMOJI,
    HOLY_FATHER_ID,
)
from core.responses import send_custom_message

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Miscellaneous Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class MiscCommands(commands.Cog):
    def __init__(self, bot : "Cordex") -> None:
        self.bot : "Cordex" = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /femboy Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_commands.command(
        name        = "femboy",
        description = "Such a good little utility kitten.",
    )
    async def cmd_femboy(self, interaction : Interaction) -> None:
        _ = await interaction.response.send_message("i-i'm such a submissive wittle kitty UwU. *snuggles* I hewp cwose proposals... naa~~")

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .super_secret_command Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "super_secret_command")
    async def cmd_super_secret_command(self, ctx : Context) -> None:
        author_id = ctx.author.id

        if author_id == BOT_OWNER_ID:
            _ = await ctx.send("This is a super super secret command that is used by people that will use it super super secretly.")
            return

        if author_id == HOLY_FATHER_ID:
            _ = await ctx.send("Hello daddy! <:puppy3:1464256700344303771> This is a super super secret command that is used by people that will use it super super secretly.")
            return

        _ = await ctx.send("Hmm… I don't think you're super super secret enough to use this super super secret command.",
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /roulette Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @app_commands.command(
        name        = "roulette",
        description = "Have fun...",
    )
    async def cmd_roulette(self, interaction : Interaction) -> None:
        guild  = interaction.guild
        member = interaction.user

        if guild is None:
            _ = await send_custom_message(
                interaction,
                msg_type = "warning",
                title    = "run command",
                subtitle = "This command can only be used in a server.",
                footer   = "Bad environment",
            )
            return

        # We don't want the cheese blud running the command.
        cheese_blud = 1167207694424350740
        if interaction.user.id == cheese_blud:
            _ = await interaction.response.send_message(
                "My developer is so fucking tired of unbanning you and adding your roles back that he has decided that you can never touch this command again. Dumbass. <:laugh5:1481288430150484111>",
            )
            return

        _ = await interaction.response.defer(ephemeral = False)

        import secrets

        chamber = secrets.randbelow(6) + 1

        if chamber == 1:
            try:
                await interaction.followup.send("<a:CatShoot:1466460098955313294> *Click,* ***BAM***.")
                await guild.ban(member, reason = "Played a stupid game, won a stupid prize.", delete_message_seconds = 0)
            except discord.Forbidden:
                await interaction.followup.send("*Click,* ***Ba***… wait… the gun's jammed!")
        else:
            await interaction.followup.send("*Click.* You live.")

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .info Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.command(name = "info")
    async def cmd_info(self, ctx : Context) -> None:
        ping = round(self.bot.latency * 1000)
        good_ping = 100
        okay_ping = 200

        match ping:
            case _ if ping < good_ping:
                emoji = ACCEPTED_EMOJI
            case _ if good_ping <= ping <= okay_ping:
                emoji = CONTESTED_EMOJI
            case _:
                emoji = DENIED_EMOJI

        start_time : float = getattr(self.bot, "start_time", time.time())
        uptime_seconds     = int(time.time() - start_time)

        hours,   remainder = divmod(uptime_seconds, 3600)
        minutes, seconds   = divmod(remainder, 60)
        days,    hours     = divmod(hours, 24)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        total_guilds = len(self.bot.guilds)

        shard_id = ctx.guild.shard_id if ctx.guild else 0

        cpu_usage = float(psutil.cpu_percent())
        ram_usage = float(psutil.virtual_memory().percent) # type: ignore[implicitAny]


        _ = await ctx.send(
            content = (
                f"{emoji} # Beep Boop,\n"
                f"**Ping:** `{ping}ms`\n"
                f"**Uptime:** `{uptime_str}`\n"
                f"**Servers:** `{total_guilds}`\n"
                f"**Shard ID:** `{shard_id}`\n"
                f"### Performance\n"
                f"**CPU Usage:** `{cpu_usage}%`\n"
                f"**RAM Usage:** `{ram_usage}%`\n\n"
                f"### Environment\n"
                f"**Library:** `discord.py v{discord.__version__}`\n"
                f"**Python:** `v{platform.python_version()}`"
            ),
        )


async def setup(bot : "Cordex") -> None:
    cog = MiscCommands(bot)
    await bot.add_cog(cog)
