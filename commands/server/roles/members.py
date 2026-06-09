import discord
from discord import app_commands

from bot import Interaction

from ._base import create_base_embed

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role members Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_members(
    interaction   : Interaction,
    role          : discord.Role,
    role_filter   : app_commands.Choice[str],
    person_filter : app_commands.Choice[str],
) -> None:
    _ = await interaction.response.defer(ephemeral = True)

    guild = interaction.guild
    if guild is None:
        return

    if role_filter.value == "whohas":
        filtered = [m for m in guild.members if role in m.roles]
    else:
        filtered = [m for m in guild.members if role not in m.roles]

    if person_filter.value == "humans":
        filtered = [m for m in filtered if not m.bot]
    elif person_filter.value == "bots":
        filtered = [m for m in filtered if m.bot]

    formatted : str = "\n".join(f"- {m.mention}" for m in filtered) if filtered else "No members found."

    embed : discord.Embed = create_base_embed(
        title       = f"Members for {role.name}",
        description = formatted,
    )
    _ = embed.add_field(
        name   = "Role Filter",
        value  = role_filter.name,
        inline = True,
    )
    _ = embed.add_field(
        name   = "Person Filter",
        value  = person_filter.name,
        inline = True,
    )
    _ = embed.set_footer(text = f"{len(filtered)} member(s) found.")

    await interaction.followup.send(embed = embed)
