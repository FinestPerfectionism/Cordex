
from discord import AllowedMentions, Role

from bot import Interaction
from constants import COLOR_GREY
from core.paginator import UnnamedPaginator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role members Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_members(
    interaction   : Interaction,
    role          : Role,
    role_filter   : str | None = "whohas",
    person_filter : str | None = None,
    *,
    ephemeral     : bool       = False,
) -> None:
    await interaction.response.defer(ephemeral = ephemeral)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    not_members = set(interaction.guild.members) - set(role.members)

    match (role_filter, person_filter):
        case ("whohas", "humans"):
            filtered = [m for m in role.members if not m.bot]
        case ("whohas", "bots"):
            filtered = [m for m in role.members if m.bot]
        case ("whohas", _):
            filtered = list(role.members)
        case (_, "humans"):
            filtered = [m for m in not_members if not m.bot]
        case (_, "bots"):
            filtered = [m for m in not_members if m.bot]
        case _:
            filtered = list(not_members)

    person_label = "Bots"   if person_filter == "bots"          else ("Humans" if person_filter == "humans" else "Members")
    role_label   = "not in" if role_filter   == "whodoesnthave" else "in"

    mention = role.mention if not role.is_default() else "@everyone"

    view = UnnamedPaginator(
        f"### {person_label} {role_label} {mention},",
        [f"- {member.mention} | {member.id}" for member in filtered] if filtered else ["No members found."],
        data_name = person_label.lower(),
        per_page  = 15,
        color     = role.color if role.color.value else COLOR_GREY,
        container = True,
    )
    view.message = await interaction.followup.send(
        view             = view,
        ephemeral        = ephemeral,
        allowed_mentions = AllowedMentions.none(),
    )
