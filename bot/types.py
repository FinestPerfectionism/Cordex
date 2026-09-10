from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, NamedTuple

from discord import StageChannel, TextChannel, Thread, VoiceChannel
from discord.app_commands import Command, Group
from discord.ext.commands import Cog  # pyright: ignore[reportMissingTypeStubs]

from constants import DisplayNameEffect, DisplayNameFont

if TYPE_CHECKING:
    from .bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Types
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type LambdaInter = Callable[["Interaction"], Awaitable[None]]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# AnnotatedCommand
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

AnnotatedCommand = Command[Group | Cog, ..., object] | Group

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
