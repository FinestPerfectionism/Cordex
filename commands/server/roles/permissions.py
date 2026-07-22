from discord import AllowedMentions, Embed, Role

from bot import Interaction
from constants import COLOR_BLURPLE

from ._base import format_permission

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server role permissions Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_server_role_permissions(
    interaction : Interaction,
    role        : Role,
    perm_filter : str | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    lines : list[str] = []
    for perm_name, value in role.permissions:
        if perm_filter == "enabled" and not value:
            continue
        if perm_filter == "disabled" and value:
            continue
        lines.append(format_permission(perm_name, value = value))

    embed = Embed(
        title       = f"Permissions for {role.name}",
        description = f"**{role.name}:**\n" + "\n".join(lines) if lines else "No permissions match this filter.",
        color       = COLOR_BLURPLE,
    )

    await interaction.followup.send(embed = embed, allowed_mentions = AllowedMentions.none())
