from typing import cast

from discord import AllowedMentions, Embed, Role

from bot import Interaction
from constants import COLOR_BLURPLE
from core.exceptions import send_bad_argument

from ._base import format_permission

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role compare Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_compare(
    interaction : Interaction,
    role_1      : Role,
    role_2      : Role,
) -> None:
    await interaction.response.defer(ephemeral = True)

    if role_1.id == role_2.id:
        await send_bad_argument(interaction, subtitle = {("role-1", "role-2") : "You cannot compare a role with itself."})
        return

    diffs_role_1 : list[str] = []
    diffs_role_2 : list[str] = []

    for perm_name, value1 in role_1.permissions:
        value2 : bool = cast("bool", getattr(role_2.permissions, perm_name))
        if value1 != value2:
            diffs_role_1.append(format_permission(perm_name, value = value1))
            diffs_role_2.append(format_permission(perm_name, value = value2))

    embed = Embed(
        title = f"Permission Differences for {role_1.name} and {role_2.name}",
        color = COLOR_BLURPLE,
    )

    if not diffs_role_1:
        embed.description = "Roles have identical permissions."
    else:
        embed.add_field(
            name   = role_1.name,
            value  = "No permissions." if role_1.permissions.value == 0 else "\n".join(diffs_role_1),
            inline = True,
        )
        embed.add_field(
            name   = role_2.name,
            value  = "No permissions." if role_2.permissions.value == 0 else "\n".join(diffs_role_2),
            inline = True,
        )

    await interaction.followup.send(embed = embed, allowed_mentions = AllowedMentions.none())
