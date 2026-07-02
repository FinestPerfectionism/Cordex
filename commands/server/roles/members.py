from discord import Embed, Role

from bot import Interaction
from constants import COLOR_BLURPLE

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role members Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_members(
    interaction   : Interaction,
    role          : Role,
    role_filter   : str,
    person_filter : str | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    guild = interaction.guild

    match (role_filter, person_filter):
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

    embed = Embed(
        title       = f"Members for {role.name}",
        description = formatted,
        color       = COLOR_BLURPLE,
    )

    role_filter_name   = "Not a Member of" if role_filter == "whodoesnthave" else "Member of"
    person_filter_name = "Both" if person_filter is None else person_filter.capitalize()

    embed.add_field(
        name   = "Role Filter",
        value  = role_filter_name,
        inline = True,
    )
    embed.add_field(
        name   = "Person Filter",
        value  = person_filter_name,
        inline = True,
    )
    embed.set_footer(text = f"{len(filtered)} member(s) found.")

    await interaction.followup.send(embed = embed)
