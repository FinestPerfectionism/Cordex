from typing import Self

from discord import ForumChannel, StageChannel, TextChannel, Thread, VoiceChannel
from discord.abc import GuildChannel
from discord.ui import Container, LayoutView, TextDisplay

from bot import Interaction
from constants import COLOR_GREY

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server channel info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_server_channel_info(interaction : Interaction, channel : GuildChannel | None = None) -> None:
    await interaction.response.defer()

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    target = channel or interaction.channel

    if not isinstance(target, TextChannel | VoiceChannel | Thread | StageChannel | ForumChannel | GuildChannel):
        return

    # ⸻ Build the view

    class InfoView(LayoutView):
        container : Container[Self] = Container[Self](
            TextDisplay(f"{target.mention} | {target.id}"),
            TextDisplay(
                (
                    ""
                ),
            ),
            accent_color = COLOR_GREY,
        )

    await interaction.followup.send(
        "This command does nothing right now. :[",
        ephemeral = True,
    )
