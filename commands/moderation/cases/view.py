# from discord import AllowedMentions
# from discord.utils import escape_markdown, format_dt

from bot import Interaction
from core.exceptions import send_bad_argument
from core.moderation import CasesManager

# from core.paginator import UnnamedPaginator
# from constants import COLOR_GREY

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation cases view Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_cases_view(interaction : Interaction, case_id : int | None = None) -> None:
    guild = interaction.guild
    if not guild:
        return

    cases_manager = CasesManager(interaction.client, guild)

    if case_id:
        case = await cases_manager.get_case(case_id)
        if not case:
            await send_bad_argument(
                interaction,
                subtitle = {"case-id" : "Case not found."},
            )
            return
    else:
        cases = await cases_manager.get_all_cases()
        if not cases:
            await send_bad_argument(
                interaction,
                subtitle = {None : "No cases found."},
            )
            return

        """
        class CasePaginator(UnnamedPaginator):
            def __init__(self) -> None:
                super().__init__(
                    "# Server Cases",
                    [
                        (
                            f"**{case.target.mention if case.target else "Unknown Member"} | {case.moderator.mention}**\n"
                            f"*{escape_markdown(case.reason)}*\n"
                            f"-# Occured at {format_dt(case.created_at, "F")}, {format_dt(case.created_at, "R")}.\n"
                            f"-# Case ID: #{case.id}"
                        ) for case in cases
                    ],
                    data_name = "Cases",
                    per_page  = 10,
                    color     = COLOR_GREY,
                    container = True,
                )

        await interaction.response.send_message(
            view             = CasePaginator(),
            ephemeral        = True,
            allowed_mentions = AllowedMentions.none(),
        )
        """
