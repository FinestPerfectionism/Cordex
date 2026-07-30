from collections.abc import Awaitable, Callable
from re import compile
from typing import Self, final

from discord import DMChannel, TextChannel, Thread, VoiceChannel
from discord.app_commands import Choice

from bot import Interaction, bot
from bot.ui import Button, View, button, green, red
from core.cog_loader import discover_cogs
from core.responses import format_message
from core.utilities import format_values

type _Inter = Callable[[Interaction], Awaitable[None]]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# TextChannelTypes
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

TextChannelTypes = (TextChannel, Thread, DMChannel, VoiceChannel)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Emoji Stuff
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

EMOJI_PATTERN = compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>")

def _inaccessible_emoji_ids(text : str) -> list[str]:
    inaccessible_ids : list[str] = []

    for match in EMOJI_PATTERN.finditer(text):
        emoji_id = int(match.group("id"))
        if bot.get_emoji(emoji_id) is None:
            inaccessible_ids.append(match.group(0))

    return inaccessible_ids

@final
class _NoEmojiAccessView(View):
    def __init__(self, on_continue : _Inter) -> None:
        super().__init__(timeout = None)
        self.on_continue = on_continue

    @button(label = "Send", style = green)
    async def btn_send(self, interaction : Interaction, _button : Button[Self]) -> None:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

        await interaction.response.edit_message(view = self)
        await self.on_continue(interaction)

    @button(label = "Abort", style = red)
    async def btn_abort(self, interaction : Interaction, _button : Button[Self]) -> None:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True

        await interaction.response.edit_message(view = self)

async def emoji_inaccessible(
    interaction : Interaction,
    text        : str,
    on_continue : _Inter,
) -> bool:
    inaccessible_ids = _inaccessible_emoji_ids(text)

    if not inaccessible_ids:
        return False

    plural = "" if len(inaccessible_ids) == 1 else "s"

    await interaction.followup.send(
        format_message(
            msg_type =  "warning",
            title    =  "run command",
            subtitle = f"I don't have access to the emoji{plural} {format_values(inaccessible_ids, wrap = "`")}.",
        ),
        view = _NoEmojiAccessView(on_continue),
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

async def cog_autocomplete(_interaction : Interaction, current : str) -> list[Choice[str]]:  # noqa: RUF029
    return [
        Choice(name = cog, value = cog)
        for cog in get_cogs() if current.lower() in cog.lower()
    ][:25]
