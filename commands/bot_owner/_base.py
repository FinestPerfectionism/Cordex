import re
from collections.abc import Awaitable, Callable
from typing import Self

import discord
from discord.app_commands import Choice
from discord.ui import Button, View, button

from bot import Interaction
from bot.ui import green, red
from constants import CONTESTED_EMOJI
from core.cog_loader import discover_cogs
from core.utilities import format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# TextChannelTypes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

TextChannelTypes = (discord.TextChannel, discord.Thread, discord.DMChannel, discord.VoiceChannel)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Emoji Stuff
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

EMOJI_PATTERN = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>")

def inaccessible_emoji_ids(client : discord.Client, text : str) -> list[str]:
    inaccessible_ids : list[str] = []

    for match in EMOJI_PATTERN.finditer(text):
        emoji_id = int(match.group("id"))
        if client.get_emoji(emoji_id) is None:
            inaccessible_ids.append(match.group(0))

    return inaccessible_ids

class NoEmojiAccessView(View):
    def __init__(self, on_continue : Callable[[Interaction], Awaitable[None]]) -> None:
        super().__init__(timeout = None)
        self.on_continue : Callable[[Interaction], Awaitable[None]] = on_continue

    @button(label = "Send", style = green)
    async def btn_send(self, interaction : Interaction, _button : Button[Self]) -> None:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

        await interaction.response.edit_message(view = self)
        await self.on_continue(interaction)

    @button(label = "End", style = red)
    async def btn_end(self, interaction : Interaction, _button : Button[Self]) -> None:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

        await interaction.response.edit_message(view = self)

async def emoji_inaccessible(
    interaction : Interaction,
    text        : str,
    on_continue : Callable[[Interaction], Awaitable[None]],
) -> bool:
    inaccessible_ids = inaccessible_emoji_ids(interaction.client, text)

    if not inaccessible_ids:
        return False

    plural = "" if len(inaccessible_ids) == 1 else "s"

    await interaction.followup.send(
        (
            f"{CONTESTED_EMOJI} **Failed to run command!**\n"
            f"I don't have access to the emoji{plural} {format_values(inaccessible_ids, wrap = "`")}."
        ),
        view = NoEmojiAccessView(on_continue),
    )

    return True

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# get_cogs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def get_cogs() -> list[str]:
    return discover_cogs("commands", "events", "core")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# cog_autocomplete
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def cog_autocomplete(_interaction : Interaction, current : str) -> list[Choice[str]]:
    return [
        Choice(name = cog, value = cog)
        for cog in get_cogs() if current.lower() in cog.lower()
    ][:25]
