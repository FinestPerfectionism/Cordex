from typing import final

from discord import AllowedMentions, Member, Role
from discord.ui import TextDisplay
from discord.utils import format_dt

from bot import Interaction
from bot.ui import Container, LayoutView
from constants import COLOR_GREY
from core.utilities import codeblock, format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server role info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_server_role_info(
    interaction : Interaction,
    role        : Role,
    *,
    ephemeral   : bool = True,
) -> None:
    await interaction.response.defer(ephemeral = ephemeral)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None or not isinstance(interaction.user, Member):
        return

    guild = interaction.guild

    roles       = sorted(guild.roles, key = lambda r : r.position)

    hierarchy_lines = ""
    for p in range(role.position + 3, role.position - 4, -1):
        if 0 <= p < len(roles):
            prefix = ">" if roles[p] == role else " "
            hierarchy_lines += f"{len(roles) - p:>4}.   {prefix} {roles[p].name}\n"

    top_role = interaction.user.top_role
    diff_string = "" if guild.default_role == top_role else (
        "This is your highest role." if role == top_role else
        f"This role is {"above" if role > top_role else "below"} your highest role."
    )

    # ⸻ Gradient checks

    if "ENHANCED_ROLE_COLORS" in guild.features and role.secondary_color:
        if role.tertiary_color:
            color = f"{role.color}-{role.secondary_color}-{role.tertiary_color} | Holographic"
        else:
            color = f"{role.color}-{role.secondary_color} | Gradient"
    else:
        color = f"{role.color} | Solid"

    # ⸻ Build the view

    @final
    class InfoView(LayoutView):
        container = Container(
            TextDisplay(f"### {role.mention} | {role.id}"),
            TextDisplay(
                format_table(
                    {
                        "Appearance"        : color,
                        "Hoisted"           : "Yes" if role.hoist else "No",
                        "Mentionable"       : "Yes" if role.mentionable else "No",
                        "Number of Members" : f"{len(role.members)}",
                        "Created at"        : f"{format_dt(role.created_at, style = "F")} | {format_dt(role.created_at, style = "R")}",
                    },
                ),
            ),
            TextDisplay(
                (
                    f"**Relative Hierarchy**\n"
                    f"{codeblock(hierarchy_lines, language = None)}"
                    f"{diff_string}"
                ),
            ),
            color = role.color if role.color.value else COLOR_GREY,
        )

    await interaction.followup.send(
        view             = InfoView(),
        ephemeral        = ephemeral,
        allowed_mentions = AllowedMentions.none(),
    )
