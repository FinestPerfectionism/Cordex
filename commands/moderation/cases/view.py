from discord import AllowedMentions, Member
from discord.utils import format_dt

from bot import Interaction
from bot.ui import (
    Container,
    LayoutView,
    TextDisplay,
    Thumbnail,
    ThumbnailSection,
    VisibleLargeSeparator,
)
from constants import COLOR_GREY
from core.exceptions import send_bad_argument
from core.moderation import Case, CasesManager
from core.paginator import UnnamedPaginator
from core.responses import FormatOverride, MessageType, format_send
from core.utilities import format_table

from ._base import format_summary

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation cases view Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def _build_view(case : Case) -> LayoutView:
    view      = LayoutView()
    container = Container[view](TextDisplay(f"# {case.action_type.readable()} | #{case.id}"), color = COLOR_GREY)

    sections : list[tuple[str, Member | None]] = [
        ("Target",    case.target),
        ("Moderator", case.moderator),
    ]

    for heading, member in sections:
        if member is None:
            continue

        member_table : dict[str, object] = {
            heading           : member.mention,
            f"{heading} Name" : member.name,
            f"{heading} ID"   : member.id,
        }
        member_info = (
            f"## {heading}\n"
            f"{format_table(member_table)}"
        )

        container.add_item(VisibleLargeSeparator())
        if member.guild_avatar:
            container.add_item(ThumbnailSection(member_info, thumbnail = Thumbnail[view](member.guild_avatar.url)))
        else:
            container.add_text(member_info)

    details : dict[str, object] = {"Expired" : case.expired}

    if case.related_case_id is not None:
        details["Related Case"] = f"#{case.related_case_id}"
    if case.seconds_to_delete is not None:
        details["Message Delete History"] = f"{case.seconds_to_delete} seconds"
    if case.timeout_length is not None:
        details["Duration"] = f"{case.timeout_length} seconds"
    if case.channel is not None:
        details["Channel"] = case.channel.mention
    if case.purge_amount is not None:
        details["Amount"] = case.purge_amount
        details["Forced"] = case.purge_force
    if case.channel is None:
        details["DM Sent"] = case.dm_user

    container.add_items(
        VisibleLargeSeparator(),
        TextDisplay(
            "## Details\n"
           f"{format_table(details)}",
        ),
        VisibleLargeSeparator(),
        TextDisplay(
            "## Reason\n"
           f"{case.reason}",
        ),
        VisibleLargeSeparator(),
        TextDisplay(f"-# Occurred at {format_dt(case.created_at, "F")}, {format_dt(case.created_at, "R")}"),
    )

    view.add_item(container)
    return view


async def run_mod_cases_view(interaction : Interaction, case_id : int | None = None) -> None:
    guild = interaction.guild
    if not guild:
        return

    cases_manager = CasesManager(interaction.client, guild)

    if case_id is not None:
        case = await cases_manager.get_case(case_id)
        if not case:
            await send_bad_argument(
                interaction,
                subtitle = {"case-id" : "Case not found."},
            )
            return

        await interaction.response.send_message(
            view             = _build_view(case),
            ephemeral        = True,
            allowed_mentions = AllowedMentions.none(),
        )
        return

    cases = list(reversed(await cases_manager.get_all_cases()))
    if not cases:
        await format_send(
            interaction,
            MessageType.warning,
            title    = "No cases found",
            override = FormatOverride(prefix = False),
        )
        return

    class CasePaginator(UnnamedPaginator):
        def __init__(self) -> None:
            super().__init__(
                "# Server Cases",
                [format_summary(case) for case in cases],
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
