from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, NamedTuple

from discord import StageChannel, TextChannel, Thread, VoiceChannel

from constants import DisplayNameEffect, DisplayNameFont

if TYPE_CHECKING:
    from .bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Types
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type LambdaInter = Callable[["Interaction"], Awaitable[None]]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Guild Messagables
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

GuildMessagable        = TextChannel | StageChannel | VoiceChannel | Thread
GuildMessagableChannel = TextChannel | StageChannel | VoiceChannel

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# NameStyleResult
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class NameStyleResult(NamedTuple):
    font_id   : DisplayNameFont
    effect_id : DisplayNameEffect
    colors    : list[str]
