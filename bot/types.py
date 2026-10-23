from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from discord import StageChannel, TextChannel, Thread, VoiceChannel
from discord.app_commands import Command, Group
from discord.ext.commands import Cog

from constants import DisplayNameEffect, DisplayNameFont

if TYPE_CHECKING:
    from typing_extensions import Sentinel as sentinel

    from .bot import Interaction
else:
    from typing_extensions import (
        sentinel,  # ⸻ For whatever reason, pyright seems to not find the 4.6.0 typing-extensions sentinel function.
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Types
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

type LambdaInter = Callable[["Interaction"], Awaitable[None]]  # ruff: ignore[quoted-type-alias]


# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# NOT_PASSED Sentinel
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

NOT_PASSED = sentinel("NOT_PASSED")

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


@dataclass(frozen = True, slots = True)
class NameStyleResult:
    font   : DisplayNameFont
    effect : DisplayNameEffect
    colors : list[str]
