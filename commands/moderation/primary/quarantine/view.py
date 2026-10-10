from discord import AllowedMentions

from bot import Interaction
from core.moderation import Actions
from core.responses import FormatOverride, MessageType, format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation quarantine view Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_primary_quarantine_view(interaction : Interaction) -> None:
    guild = interaction.guild
    if not guild:
        return

    actions = Actions(interaction.client, guild)
    paginator = await actions.quarantine_view()
    if not paginator:
        await format_send(
            interaction,
            MessageType.success,
            title    = "No members are quarantined",
            override = FormatOverride(prefix = False),
        )
        return

    await interaction.response.send_message(
        view             = paginator,
        ephemeral        = True,
        allowed_mentions = AllowedMentions.none(),
    )
