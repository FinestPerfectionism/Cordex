from discord import Member

from bot import Interaction
from commands.moderation.primary._base import send_moderation_modal
from core.moderation import ActionType

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation timeout add Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_primary_timeout_add(interaction : Interaction, target : Member) -> None:
    await send_moderation_modal(interaction, ActionType.timeout_add, target)
