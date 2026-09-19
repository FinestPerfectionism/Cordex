from discord import __version__
from platform import python_version
from typing import Self, final

from bot import Interaction
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLUE
from core.utilities import format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /about Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

"""
     Owner: leothelion_
    Admins: leothelion_, 0lante, jetraidz
 Developer: finestperfectionism
   Version: v6.4.3 [LuaTeX]
    Guilds: 40
   Members: 3763
  Commands: 70
    Uptime: 65 days 11 hours
 CPU Usage: 0.4%
    Memory: 2739/15860 MiB (17.3%)
    Python: 3.14.7+  (discord.py: 2.7.1)
        OS: openSUSE Tumbleweed 20260815
    Kernel: Linux-7.1.3-1-default-x86_64-with-glibc2.43
   TeXLive: 79639 (tlmgr: 2 months ago)
    LuaTeX: 1.24.0 (TeX Live 2026)
     Typst: 0.15.1
"""


async def run_about(interaction : Interaction) -> None:
    client = interaction.client

    await interaction.response.defer()

    owners = client.developers
    s = "s" if len(owners) > 1 else ""

    @final
    class AboutView(LayoutView):
        container = Container[Self](
            TextDisplay("# About Me,"),
            VisibleLargeSeparator(),
            TextDisplay(
                format_table(
                    {
                       f"Owner{s}"   : ", ".join(owner.name for owner in owners),
                        "Version"    : client.version,
                        "Guilds"     : len(client.guilds),
                        "Members"    : sum(guild.member_count for guild in client.guilds),
                        "Commands"   : ...,
                        "Memory"     : ...,
                        "Python"     : python_version(),
                        "Discord.py" : __version__,
                    },
                ),
            ),
            color = COLOR_BLUE,
        )

    await interaction.followup.send(view = AboutView())
