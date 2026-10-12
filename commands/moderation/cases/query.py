from datetime import UTC, datetime

from discord import AllowedMentions, Member, User

from bot import Interaction
from bot.types import GuildMessagableChannel
from constants import COLOR_GREY
from core.exceptions import send_bad_argument
from core.moderation import ActionType, CasesManager
from core.paginator import UnnamedPaginator
from core.responses import FormatOverride, MessageType, format_send

from ._base import build_case_section

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
    before      : str                    | None = None,
    after       : str                    | None = None,
) -> None:
    """
    Query moderation cases with various filters.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    action_type : `str | None = None`
        Filter by action type.
    moderator : `Member | None = None`
        Filter by moderator.
    target : `User | None = None`
        Filter by user.
    channel : `GuildMessagableChannel | None = None`
        Filter by channel.
    expired : `bool | None = None`
        Filter by expiration.
    before : `str | None = None`
        Filter cases that occurred before this date. Must be of the form "MM/DD/YYYY".
    after : `str | None = None`
        Filter cases that occurred after this date. Must be of the form "MM/DD/YYYY".
    """
    guild = interaction.guild
    if not guild:
        return

    if all(case_filter is None for case_filter in (action_type, moderator, target, channel, expired)):
        await send_bad_argument(
            interaction,
            subtitle = {None : "At least one filter must be chosen."},
        )
        return

    if before:
        try:
            before_datetime = datetime.strptime(before, "%m/%d/%Y").replace(tzinfo = UTC)
        except ValueError:
            await send_bad_argument(
                interaction,
                subtitle = {"before" : "Invalid date passed. A date must be of the form `MM/DD/YYYY`."},
            )
            return
    else:
        before_datetime = None

    if after:
        try:
            after_datetime = datetime.strptime(after, "%m/%d/%Y").replace(tzinfo = UTC)
        except ValueError:
            await send_bad_argument(
                interaction,
                subtitle = {"after" : "Invalid date passed. A date must be of the form `MM/DD/YYYY`."},
            )
            return
    else:
        after_datetime = None

    parsed_action = ActionType(action_type) if action_type is not None else None
    if channel is not None and parsed_action != ActionType.purge:
        await send_bad_argument(
            interaction,
            subtitle = {("action-type", "channel") : "`channel` cannot be passed if `action-type` is not 'Purge'."},
        )
        return

    cases_manager = CasesManager(interaction.client, guild)
    cases         = list(
        reversed(
            await cases_manager.filter_by(
                action_type  = parsed_action,
                moderator_id = moderator.id if moderator else None,
                target_id    = target.id    if target    else None,
                channel_id   = channel.id   if channel   else None,
                expired      = expired,
                before       = before_datetime,
                after        = after_datetime,
            ),
        ),
    )

    if expired is False:
        cases = [
            case for case in cases if
            case.action_type not in {
                ActionType.ban_remove,
                ActionType.quarantine_remove,
                ActionType.timeout_remove,
            }
        ]

    if not cases:
        await format_send(
            interaction,
            MessageType.warning,
            title    = "No cases found matching this filter",
            override = FormatOverride(prefix = False),
        )
        return

    class CasePaginator(UnnamedPaginator):
        def __init__(self) -> None:
            super().__init__(
                "# Cases Found",
                [build_case_section(case, cases_manager) for case in cases],
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
