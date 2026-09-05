from typing import Literal, Self, final

from discord import AllowedMentions, Role

from bot import Interaction
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_GREY

from ._base import format_permission

type PermissionsFilter = Literal["Both", "Enabled", "Disabled"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role permissions Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_permissions(
    interaction : Interaction,
    role        : Role,
    perm_filter : PermissionsFilter = "Both",
) -> None:
    await interaction.response.defer()

    lines : list[str] = []
    for name, value in role.permissions:
        if perm_filter == "Enabled" and not value:
            continue

        if perm_filter == "Disabled" and value:
            continue

        lines.append(format_permission(name, value = value))

    # ⸻ Mentions.

    role_mention = role.mention if not role.is_default() else "@everyone"

    match perm_filter:
        case "Both":
            filter_mention = ""
        case "Enabled":
            filter_mention = "Enabled "
        case "Disabled":
            filter_mention = "Disabled "

    p = "p" if filter_mention else "P"

    # ⸻ Build the view.

    @final
    class PermissionsView(LayoutView):
        container = Container[Self](
            TextDisplay(f"### {filter_mention}{p}ermissions for {role_mention},"),
            VisibleLargeSeparator(),
            TextDisplay("\n".join(lines) if lines else "No permissions found."),
            color = role.color if role.color.value else COLOR_GREY,
        )

    await interaction.followup.send(
        view             = PermissionsView(),
        allowed_mentions = AllowedMentions.none(),
    )
