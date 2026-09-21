from platform import python_version
from typing import Self, final

from discord import __version__ as DISCORD_VERSION  # ruff: ignore[lowercase-imported-as-non-lowercase]

from bot import Interaction
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_BLUE
from core.utilities import format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /about Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


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
                       f"Owner{s}"    : ", ".join(owner.name for owner in owners),
                        "Bot Version" : client.version,
                        "Guilds"      : len(client.guilds),
                        "Members"     : sum(guild.member_count or 0 for guild in client.guilds),
                        "Commands"    : len(client.get_commands_cache()),
                        "Latency"     : client.latency * 100,
                        "Python"      : python_version(),
                        "Discord.py"  : DISCORD_VERSION,
                    },
                ),
            ),
            color = COLOR_BLUE,
        )

    await interaction.followup.send(view = AboutView())
