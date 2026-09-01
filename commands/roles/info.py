from typing import Self, final

from discord import AllowedMentions, Asset, Member, Role
from discord.ui import Thumbnail
from discord.utils import format_dt

from bot import Interaction
from bot.ui import Container, LayoutView, TextDisplay, ThumbnailSection
from constants import COLOR_GREY
from core.utilities import codeblock, format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_info(interaction : Interaction, role : Role) -> None:
    await interaction.response.defer()

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None or not isinstance(interaction.user, Member):
        return

    guild = interaction.guild

    roles = sorted(guild.roles, key = lambda r : r.position)
    hierarchy_lines = ""

    for p in range(role.position + 3, role.position - 4, -1):
        if 0 <= p < len(roles):
            prefix = ">" if roles[p] == role else " "
            hierarchy_lines += f"{len(roles) - p:>4}.   {prefix} {roles[p].name}\n"

    top_role = interaction.user.top_role

    diff = "" if guild.default_role == top_role else (
        "This is your highest role."
        if role == top_role else
        f"This role is {"above" if role > top_role else "below"} your highest role."
    )

    # ⸻ Gradient checks.

    enhanced_role = bool("ENHANCED_ROLE_COLORS" in guild.features and role.secondary_color)

    color = (
        f"{role.color}-{role.secondary_color}-{role.tertiary_color} | Holographic"
        if role.tertiary_color else
        f"{role.color}-{role.secondary_color} | Gradient"
    ) if enhanced_role else f"{role.color} | Solid"

    # ⸻ Build the view.

    table = TextDisplay["InfoView"](
        format_table(
            {
                "Appearance"        : color,
                "Hoisted"           :  "Yes" if role.hoist else "No",
                "Mentionable"       :  "Yes" if role.mentionable else "No",
                "Number of Members" : f"{len(role.members)}",
                "Created at"        : f"{format_dt(role.created_at, style = "F")} | {format_dt(role.created_at, style = "R")}",
            },
        ),
    )

    hierarchy = TextDisplay["InfoView"](
        (
            f"**Relative Hierarchy**\n"
            f"{codeblock(hierarchy_lines, language = None)}"
        ),
    )

    icon_url = role.display_icon.url if isinstance(role.display_icon, Asset) else None

    @final
    class InfoView(LayoutView):
        container = Container[Self](
            TextDisplay(f"### {role.mention} | {role.id}"),
            color = role.color if role.color.value else COLOR_GREY,
        )

        if diff:
            container.add_item(TextDisplay(diff))

        if icon_url:
            container.add_item(ThumbnailSection(table, thumbnail = Thumbnail(icon_url)))
        else:
            container.add_item(table)

        container.add_item(hierarchy)

    await interaction.followup.send(
        view             = InfoView(),
        allowed_mentions = AllowedMentions.none(),
    )
