from typing import cast

from discord import Embed, Role

from bot import Interaction
from constants import COLOR_BLURPLE

from ._base import format_permission

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role permissions-compare Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_permissionscompare(
    interaction : Interaction,
    role1       : Role,
    role2       : Role,
) -> None:
    _ = await interaction.response.defer(ephemeral = False)

    diffs_role1 : list[str] = []
    diffs_role2 : list[str] = []

    for perm_name, value1 in role1.permissions:
        value2 : bool = cast(bool, getattr(role2.permissions, perm_name))
        if value1 != value2:
            diffs_role1.append(format_permission(perm_name, value = value1))
            diffs_role2.append(format_permission(perm_name, value = value2))

    embed = Embed(
        title = f"Permission Differences for {role1.name} and {role2.name}",
        color = COLOR_BLURPLE,
    )

    if not diffs_role1:
        embed.description = "Roles have identical permissions."
    else:
        _ = embed.add_field(
            name   = role1.name,
            value  = "\n".join(diffs_role1),
            inline = True,
        )
        _ = embed.add_field(
            name   = role2.name,
            value  = "\n".join(diffs_role2),
            inline = True,
        )

    await interaction.followup.send(embed = embed)
