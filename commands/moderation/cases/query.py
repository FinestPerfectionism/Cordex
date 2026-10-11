from discord import AllowedMentions, Member, User
from discord.utils import escape_markdown, format_dt

from bot import Interaction
from bot.types import GuildMessagableChannel
from constants import COLOR_GREY
from core.exceptions import send_bad_argument
from core.moderation import ActionType, CasesManager
from core.paginator import UnnamedPaginator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation cases query Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_mod_cases_query(
    interaction : Interaction,
    *,
    action_type : str                    | None = None,
    moderator   : Member                 | None = None,
    target      : User                   | None = None,
    channel     : GuildMessagableChannel | None = None,
    expired     : bool                   | None = None,
) -> None:
    guild = interaction.guild
    if not guild:
        return

    if channel and action_type != ActionType.purge:
        await send_bad_argument(
            interaction,
            subtitle = {("action-type", "channel") : "`channel` cannot be passed if `action-type` is not `Purge`."},
        )
        return

    cases = await CasesManager(interaction.client, guild).filter_by(
        action_type  = ActionType(action_type),
        moderator_id = moderator.id if moderator else None,
        target_id    = target.id    if target    else None,
        channel_id   = channel.id   if channel   else None,
        expired      = expired,
    )

    class CasePaginator(UnnamedPaginator):  # TODO: Handle purge-type cases.
        def __init__(self) -> None:
            super().__init__(
                "# Cases Found",
                [
                    (
                        f"**{case.target.mention if case.target else "Unknown Member"} | {case.moderator.mention}**\n"
                        f"*{escape_markdown(case.reason)}*\n"
                        f"-# Occurred at {format_dt(case.created_at, "F")}, {format_dt(case.created_at, "R")}.\n"
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
