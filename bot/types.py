from typing import TYPE_CHECKING, NamedTuple

from discord import StageChannel, TextChannel, Thread, VoiceChannel

if TYPE_CHECKING:
    from constants import DisplayNameEffect, DisplayNameFont

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Types
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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
