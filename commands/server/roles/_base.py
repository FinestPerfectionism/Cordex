import discord

from constants import ACCEPTED_EMOJI, COLOR_BLURPLE, DENIED_EMOJI

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Role Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def create_base_embed(title : str, description : str | None = None) -> discord.Embed:
    return discord.Embed(
        title       = title,
        description = description,
        color       = COLOR_BLURPLE,
    )

def format_permission(perm_name : str, *, value : bool) -> str:
    label = perm_name.replace("_", " ").title()
    mark  = ACCEPTED_EMOJI if value else DENIED_EMOJI
    return f"- {label} {mark}"
