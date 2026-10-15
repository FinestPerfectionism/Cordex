from discord import AllowedMentions

from bot import Interaction
from core.moderation import Actions
from core.responses import FormatOverride, MessageType, format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation ban view Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_moderation_ban_view(interaction : Interaction) -> None:
    """
    View all banned members.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    """
    guild = interaction.guild
    if not guild:
        return

    actions = Actions(interaction.client, guild)
    paginator = await actions.ban_view()
    if not paginator:
        await format_send(
            interaction,
            MessageType.success,
            title    = "No members are banned",
            override = FormatOverride(prefix = False),
        )
        return

    await interaction.response.send_message(
        view             = paginator,
        ephemeral        = True,
        allowed_mentions = AllowedMentions.none(),
    )
