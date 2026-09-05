from typing import Literal

from discord import AllowedMentions, Role

from bot import Interaction
from constants import COLOR_GREY
from core.paginator import UnnamedPaginator

type PersonFilter = Literal["Both", "Humans", "Bots"]
type RoleFilter   = Literal["In", "Not In"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /role members Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_role_members(
    interaction   : Interaction,
    role          : Role,
    role_filter   : RoleFilter   = "In",
    person_filter : PersonFilter = "Both",
    *,
    ephemeral     : bool         = False,
) -> None:
    await interaction.response.defer(ephemeral = ephemeral)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    # ⸻ Resolve the list.

    not_members = set(interaction.guild.members) - set(role.members)
    members     = role.members

    source      = members if role_filter == "In" else not_members

    match person_filter:
        case "Both":
            filtered = list(source)
        case "Humans":
            filtered = [m for m in source if not m.bot]
        case "Bots":
            filtered = [m for m in source if m.bot]

    # ⸻ Labels.

    person_label = "Bots"   if person_filter == "Bots"   else ("Humans" if person_filter == "Humans" else "Members")
    role_label   = "not in" if role_filter   == "Not In" else "in"

    mention = role.mention if not role.is_default() else "@everyone"

    # ⸻ Build the paginator.

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
