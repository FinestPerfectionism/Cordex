
from typing import Self, final

from discord import AllowedMentions, Role

from bot import Interaction
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import COLOR_GREY

from ._base import format_permission

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role permissions Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_permissions(
    interaction : Interaction,
    role        : Role,
    perm_filter : str | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    lines : list[str] = []
    for name, value in role.permissions:
        if perm_filter == "enabled" and not value:
            continue

        if perm_filter == "disabled" and value:
            continue

        lines.append(format_permission(name, value = value))

    role_mention = role.mention if not role.is_default() else "@everyone"

    match perm_filter:
        case "enabled":
            filter_mention = "Enabled "
        case "disabled":
            filter_mention = "Disabled "
        case None:
            filter_mention = ""
        case _:
            filter_mention = ""

    p = "p" if filter_mention else "P"

    @final
    class PermissionsView(LayoutView):
        container = Container[Self](
            TextDisplay(f"### {filter_mention}{p}ermissions for {role_mention},"),
            VisibleLargeSeparator(),
            TextDisplay("\n".join(lines) if lines else "No permissions match this filter."),
            color = role.color if role.color.value else COLOR_GREY,
        )

    await interaction.followup.send(
        view             = PermissionsView(),
        allowed_mentions = AllowedMentions.none(),
    )
