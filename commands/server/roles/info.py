from typing import Self

from discord import Member, Role
from discord.ui import LayoutView, Container, TextDisplay
from discord.utils import format_dt

from bot import Interaction
from core.utilities import codeblock
from constants import COLOR_GREY

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_info(interaction : Interaction, role : Role):
    await interaction.response.defer()
    
    # ⸻ We know that the command will run in a guild but the type checker doesn't...
    
    if interaction.guild is None or not isinstance(interaction.user, Member):
        return

    guild = interaction.guild
    
    roles       = sorted(guild.roles, key = lambda r : r.position)
    created_ago = format_dt(role.created_at, style = "F") if role.created_at else "Unknown"
    
    hierarchy_lines = ""
    for p in range(role.position + 3, role.position - 4, -1):
        if 0 <= p < len(roles):
            prefix = ">" if roles[p] == role else " "
            hierarchy_lines += f"{len(roles) - p:>4}.   {prefix} {roles[p].name}\n"
    
    top_role = interaction.user.top_role
    diff_string = "" if guild.default_role == top_role else (
        f"This is your highest role." if role == top_role else 
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
    
    class InfoView(LayoutView):
        container : Container[Self] = Container[Self](
            TextDisplay(f"### {role.mention} | {role.id}"),
            TextDisplay(
                (
                    f"`       Appearance:` {color}\n"
                    f"`          Hoisted:` {"Yes" if role.hoist else "No"}\n"
                    f"`      Mentionable:` {"Yes" if role.mentionable else "No"}\n"
                    f"`Number of members:` {len(role.members)}\n"
                    f"`       Created at:` {created_ago}\n"
                )
            ),
            TextDisplay(
                (
                    f"**Relative Hierarchy**\n"
                    f"{codeblock(hierarchy_lines, language = "")}"
                    f"{diff_string}"
                )
            ),
            accent_color = role.color if role.color.value else COLOR_GREY
        )
    
    await interaction.followup.send(view = InfoView(), ephemeral = True)