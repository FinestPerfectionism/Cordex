from discord import AllowedMentions, Role

from bot import Interaction
from constants import COLOR_GREY
from core.paginator import Paginator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role members Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_members(
    interaction   : Interaction,
    role          : Role,
    role_filter   : str | None = None,
    person_filter : str | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    actual_role_filter = role_filter or "whohas"

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    guild = interaction.guild

    match (actual_role_filter, person_filter):
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

    person_label = "Bots"   if person_filter      == "bots"          else ("Humans" if person_filter == "humans" else "Members")
    role_label   = "not in" if actual_role_filter == "whodoesnthave" else "in"

    _view = Paginator(
        f"### {person_label} {role_label} {role.mention}",
        [f"- {m.mention}" for m in filtered] if filtered else ["No members found."],
        data_name = person_label.lower(),
        per_page  = 15,
        color     = role.color if role.color.value else COLOR_GREY,
        container = True,
    )

    await interaction.followup.send(
        view             = _view,
        ephemeral        = True,
        allowed_mentions = AllowedMentions.none(),
    )
