import re
from typing import Self, final

from bot import Interaction, bot
from bot.types import LambdaInter
from bot.ui import Button, View, button, green, red
from core.cog_loader import discover_cogs
from core.exceptions import send_bad_permissions_command
from core.permissions import is_bot_owner
from core.responses import format_message
from core.utilities import format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Emoji Stuff
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

EMOJI_PATTERN = re.compile(r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>")

def _inaccessible_emoji_ids(text : str) -> list[str]:
    inaccessible_ids : list[str] = []

    for match in EMOJI_PATTERN.finditer(text):
        emoji_id = int(match.group("id"))
        if bot.get_emoji(emoji_id) is None:
            inaccessible_ids.append(match.group(0))

    return inaccessible_ids

@final
class _NoEmojiAccessView(View):
    def __init__(self, on_continue : LambdaInter) -> None:
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
    on_continue : LambdaInter,
) -> bool:
    inaccessible_ids = _inaccessible_emoji_ids(text)

    if not inaccessible_ids:
        return False

    s = "" if len(inaccessible_ids) == 1 else "s"

    await interaction.followup.send(
        format_message(
            msg_type =  "warning",
            title    =  "run command",
            subtitle = f"I don't have access to the emoji{s} {format_values(inaccessible_ids, wrap = "`")}.",
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
# Raw Bot-Owner Check
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def check_if_bo(interaction : Interaction) -> bool:
    if is_bot_owner(interaction.user):
        return True

    await send_bad_permissions_command(interaction)
    return False
