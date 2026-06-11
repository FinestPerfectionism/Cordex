import discord
from discord.app_commands import Choice

from bot import Interaction

from ._base import create_base_embed

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role members Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_members(
    interaction   : Interaction,
    role          : discord.Role,
    role_filter   : Choice[str],
    person_filter : Choice[str],
) -> None:
    _ = await interaction.response.defer(ephemeral = True)

    guild = interaction.guild
    if guild is None:
        return

    match (role_filter.value, person_filter.value):
        case ("whohas", "humans"):
            filtered = [m for m in guild.members if role in m.roles and not m.bot]

        case ("whohas", "bots"):
            filtered = [m for m in guild.members if role in m.roles and m.bot]

        case ("whohas", _):
            filtered = [m for m in guild.members if role in m.roles]

        case (_, "humans"):
            filtered = [m for m in guild.members if role not in m.roles and not m.bot]

        case (_, "bots"):
            filtered = [m for m in guild.members if role not in m.roles and m.bot]

        case _:
            filtered = [m for m in guild.members if role not in m.roles]


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
