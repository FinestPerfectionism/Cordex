from typing import cast

from discord import AllowedMentions, Embed, Role

from bot import Interaction
from constants import COLOR_BLURPLE
from core.exceptions import send_bad_argument

from ._base import format_permission

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server role permissions-compare Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_server_role_permissionscompare(
    interaction : Interaction,
    role1       : Role,
    role2       : Role,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if role1.id == role2.id:
        await send_bad_argument(interaction, subtitle = {("role-1", "role-2") : "You cannot compare a role with itself."})
        return

    diffs_role1 : list[str] = []
    diffs_role2 : list[str] = []

    for perm_name, value1 in role1.permissions:
        value2 : bool = cast(bool, getattr(role2.permissions, perm_name))
        if value1 != value2:
            diffs_role1.append(format_permission(perm_name, value = value1))
            diffs_role2.append(format_permission(perm_name, value = value2))

    embed = Embed(
        title = f"Permission Differences for {role1.mention} and {role2.mention}",
        color = COLOR_BLURPLE,
    )

    if not diffs_role1:
        embed.description = "Roles have identical permissions."
    else:
        embed.add_field(
            name   = role1.mention,
            value  = "\n".join(diffs_role1),
            inline = True,
        )
        embed.add_field(
            name   = role2.mention,
            value  = "\n".join(diffs_role2),
            inline = True,
        )

    await interaction.followup.send(embed = embed, allowed_mentions = AllowedMentions.none())
