from bot import Interaction

from .select import ActionType, ModerationTargetView

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Utilites Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def send_target_view(interaction : Interaction, action_type : ActionType) -> None:
    await interaction.response.send_message(view = ModerationTargetView(action_type), ephemeral = True)
