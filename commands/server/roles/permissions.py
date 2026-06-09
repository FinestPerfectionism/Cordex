import discord

from bot import Interaction

from ._base import create_base_embed, format_permission

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role permissions Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_permissions(
    interaction : Interaction,
    role        : discord.Role,
    perm_filter : str = "all",
) -> None:
    _ = await interaction.response.defer(ephemeral = False)

    lines : list[str] = []
    for perm_name, value in role.permissions:
        if perm_filter == "enabled" and not value:
            continue
        if perm_filter == "disabled" and value:
            continue
        lines.append(format_permission(perm_name, value = value))

    embed : discord.Embed = create_base_embed(
        title       = f"Permissions for {role.name}",
        description = f"**{role.name}:**\n" + "\n".join(lines) if lines else "No permissions match this filter.",
    )

    await interaction.followup.send(embed = embed)
