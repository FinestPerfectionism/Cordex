from dataclasses import dataclass
from typing import final

from discord import AllowedMentions, Color, Forbidden, Guild, HTTPException, Member

from bot import Cordex, log
from bot.types import GuildMessagable
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import (
    COLOR_BLACK,
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_GREY,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_YELLOW,
)
from core.utilities import format_now, format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cases Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Action Payloads
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@dataclass
class _BaseRemovePayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class _BaseAddPayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class _BaseLockdownPayload:
    moderator : Member
    target    : GuildMessagable
    reason    : str


@dataclass
class LockdownAddPayload(_BaseLockdownPayload):
    """
    Represents a lockdown add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the lockdown add.
    target : `GuildMessagable`
        The target channel of the lockdown add.
    reason : `str`
        The reason for the lockdown add.
    """


@dataclass
class LockdownRemovePayload(_BaseLockdownPayload):
    """
    Represents a lockdown remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the lockdown remove.
    target : `GuildMessagable`
        The target channel of the lockdown remove.
    reason : `str`
        The reason for the lockdown remove.
    """


@dataclass
class BanAddPayload(_BaseAddPayload):
    """
    Represents a ban add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the ban add.
    target : `Member`
        The target member of the ban add.
    reason : `str`
        The reason for the ban add.
    dm_user : `bool`
        Whether the user was direct messaged.
    seconds_to_delete : `int`
        The duration in seconds of messages to delete.
    """

    seconds_to_delete : int


@dataclass
class BanRemovePayload(_BaseRemovePayload):
    """
    Represents a ban remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the ban remove.
    target : `Member`
        The target member of the ban remove.
    reason : `str`
        The reason for the ban remove.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class KickPayload:
    """
    Represents a kick action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the kick.
    target : `Member`
        The target member of the kick.
    reason : `str`
        The reason for the kick.
    dm_user : `bool`
        Whether the user was direct messaged.
    """

    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class TimeoutAddPayload(_BaseAddPayload):
    """
    Represents a timeout add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the timeout add.
    target : `Member`
        The target member of the timeout add.
    reason : `str`
        The reason for the timeout add.
    dm_user : `bool`
        Whether the user was direct messaged.
    length : `int`
        The duration of the timeout in seconds.
    """

    length : int


@dataclass
class TimeoutRemovePayload(_BaseRemovePayload):
    """
    Represents a timeout remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the timeout remove.
    target : `Member`
        The target member of the timeout remove.
    reason : `str`
        The reason for the timeout remove.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class QuarantineAddPayload(_BaseAddPayload):
    """
    Represents a quarantine add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the quarantine add.
    target : `Member`
        The target member of the quarantine add.
    reason : `str`
        The reason for the quarantine add.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class QuarantineRemovePayload(_BaseRemovePayload):
    """
    Represents a quarantine remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the quarantine remove.
    target : `Member`
        The target member of the quarantine remove.
    reason : `str`
        The reason for the quarantine remove.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class PurgePayload:
    """
    Represents a purge action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the purge.
    target : `Member | None`
        The optional target member whose messages were purged.
    reason : `str`
        The reason for the purge.
    channel : `GuildMessagable`
        The target channel of the purge.
    amount : `int`
        The amount of messages purged.
    force : `bool`
        Whether the purge was forced.
    """

    moderator : Member
    target    : Member | None
    reason    : str
    channel   : GuildMessagable
    amount    : int
    force     : bool


Payloads = (
    LockdownAddPayload
    | LockdownRemovePayload
    | BanAddPayload
    | BanRemovePayload
    | KickPayload
    | QuarantineAddPayload
    | QuarantineRemovePayload
    | TimeoutAddPayload
    | TimeoutRemovePayload
    | PurgePayload
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cases Class
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@dataclass(frozen = True)
class _CaseData:
    color : Color
    title : str


CASE_MAP : dict[type, _CaseData] = {
    LockdownAddPayload      : _CaseData(COLOR_GREY,   "Lockdown Added"),
    LockdownRemovePayload   : _CaseData(COLOR_GREEN,  "Lockdown Removed"),
    BanAddPayload           : _CaseData(COLOR_BLACK,  "Member Ban Added"),
    BanRemovePayload        : _CaseData(COLOR_GREEN,  "Member Ban Removed"),
    KickPayload             : _CaseData(COLOR_RED,    "Member Kicked"),
    QuarantineAddPayload    : _CaseData(COLOR_ORANGE, "Member Quarantine Added"),
    QuarantineRemovePayload : _CaseData(COLOR_GREEN,  "Member Quarantine Removed"),
    TimeoutAddPayload       : _CaseData(COLOR_YELLOW, "Member Timeout Added"),
    TimeoutRemovePayload    : _CaseData(COLOR_GREEN,  "Member Timeout Removed"),
    PurgePayload            : _CaseData(COLOR_BLUE,   "Messages Purged"),
}


@final
class Cases:
    """
    Represents a guild's cases.

    Parameters
    ----------
    bot : `Cordex`
        The bot instance.
    guild : `Guild`
        The guild in which cases are being handled.
    """

    __slots__ = ("bot", "guild")

    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot   = bot
        self.guild = guild

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # _log_failure
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    def _log_failure(self, msg : str, /, *, rate_limited : bool = False) -> None:
        rate_limited_msg = " — Rate-limited" if rate_limited else ""
        log.exception("Failure during %s in guild %s, %s%s", msg, self.guild.name, self.guild.id, rate_limited_msg)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # create_case
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def create_case(self, case : Payloads) -> bool:
        """
        Create and log a case based off of a payload.

        Parameters
        ----------
        case : `Payloads`
            The payload to create the case for.

        Returns
        -------
        `bool`
            Whether the case creation was successful or not.
        """
        log_channel = await self.bot.config(self.guild).get_moderation_logging_channel()
        if not log_channel:
            return False

        data = CASE_MAP[type(case)]

        view = LayoutView()
        container = Container[view](
            TextDisplay(f"# {data.title}"),
            color = data.color,
        )

        if isinstance(case, PurgePayload):
            if case.target is not None:
                target_info = {
                    "Target"    : case.target.mention,
                    "Name"      : case.target.name,
                    "Target ID" : case.target.id,
                }

                container.add_items(
                    VisibleLargeSeparator(),
                    TextDisplay(
                        "## Target\n"
                       f"{format_table(target_info)}",
                    ),
                )
        else:
            target = case.target
            target_info = {
                "Target"    : target.mention,
                "Name"      : getattr(target, "name", str(target)),
                "Target ID" : target.id,
            }

            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Target\n"
                   f"{format_table(target_info)}",
                ),
            )

        moderator = case.moderator
        moderator_info = {
            "Moderator"      : moderator.mention,
            "Moderator Name" : moderator.name,
            "Moderator ID"   : moderator.id,
        }

        container.add_items(
            VisibleLargeSeparator(),
            TextDisplay(
                "## Moderator\n"
               f"{format_table(moderator_info)}",
            ),
        )

        details : dict[str, object] = {}

        if isinstance(case, BanAddPayload):
            details["Message Delete History"] = f"{case.seconds_to_delete} seconds"
        elif isinstance(case, TimeoutAddPayload):
            details["Duration"] = f"{case.length} seconds"
        elif isinstance(case, PurgePayload):
            details["Channel"] = case.channel.mention
            details["Amount"]  = case.amount
            details["Forced"]  = case.force

        if isinstance(case, _BaseAddPayload | _BaseRemovePayload | KickPayload):
            details["DM Sent"] = case.dm_user

        if details:
            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Details\n"
                   f"{format_table(details)}",
                ),
            )

        container.add_items(
            VisibleLargeSeparator(),
            TextDisplay(
                "## Reason\n"
               f"{case.reason}",
            ),
        )

        container.add_items(
            VisibleLargeSeparator(),
            TextDisplay(f"-# {format_now()} | {format_now("R")}"),
        )

        view.add_item(container)

        try:
            await log_channel.send(
                view             = view,
                allowed_mentions = AllowedMentions.none(),
            )
        except Forbidden:
            return False
        except HTTPException:
            self._log_failure("case logging")
            return False
        else:
            return True

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_case
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_case(self, _case : int) -> None:
        """
        Get a case.

        Parameters
        ----------
        _case : `int`
            The ID of the case to get.
        """

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # edit_case
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def edit_case(self, _case : int) -> None:
        """
        Edits a case.

        Parameters
        ----------
        _case : `int`
            The ID of the case to edit.
        """
