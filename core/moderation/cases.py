from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast, final

from discord import AllowedMentions, Color, Forbidden, Guild, HTTPException, Member

from bot import Cordex, log
from bot.types import GuildMessagable
from bot.ui import (
    Container,
    LayoutView,
    TextDisplay,
    Thumbnail,
    ThumbnailSection,
    VisibleLargeSeparator,
)
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

from .payloads import (
    BanAddPayload,
    BanRemovePayload,
    KickPayload,
    LockdownAddPayload,
    LockdownRemovePayload,
    Payloads,
    PurgePayload,
    QuarantineAddPayload,
    QuarantineRemovePayload,
    TimeoutAddPayload,
    TimeoutRemovePayload,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Cases Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

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


@dataclass(frozen = True, slots = True)
class _CreateCaseResult:
    successful : bool
    case       : Case | None


@dataclass(frozen = True, slots = True)
class Case:
    """
    Represents a moderation case.

    Parameters
    ----------
    id : `int`
        The ID of the case.
    action_type : `str`
        The type of the case.
    moderator : `Member`
        The moderator of the case.
    target : `Member | None`
        The target of the case.
    reason : `str`
        The reason for the action in the case.
    channel : `GuildMessagable | None`
        The channel affected in the case.
    created_at : `datetime`
        The datetime of when the case was created.
    dm_user : `bool | None`
        Whether the user was DMed upon the action in the case.
        Only populated in member-type cases.
    seconds_to_delete : `int | None`
        The seconds to delete upon ban in the case.
        Only populated in ban cases.
    timeout_length : `int | None`
        The length of the timeout.
        Only populated in timeout cases.
    purge_amount : `int | None`
        The amount of messages purged in the case.
        Only populated in purge cases.
    purge_force : `bool | None`
        Whether the channel was force purged in the case.
        Only populated in purge cases.
    expired : `bool`
    related_case_id : `int | None`
    """

    id                : int
    action_type       : str
    moderator         : Member
    target            : Member          | None
    reason            : str
    channel           : GuildMessagable | None
    created_at        : datetime
    dm_user           : bool            | None
    seconds_to_delete : int             | None
    timeout_length    : int             | None
    purge_amount      : int             | None
    purge_force       : bool            | None
    expired           : bool
    related_case_id   : int             | None


@final
class CasesManager:
    """
    A manager for cases operations.

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

    async def create_case(self, payload : Payloads, /) -> _CreateCaseResult:
        """
        Create and log a case based off of a payload.

        Parameters
        ----------
        payload : `Payloads`
            The payload to create the case for.
        /

        Returns
        -------
        `CreateCaseResult`
            The case created (`.case`) as well as a boolean status of whether the logging *and* database creation were succesful (`.successful`). A case can still be created while `.successful` is False.
        """
        log_channel = await self.bot.config(self.guild).get_moderation_logging_channel()
        if not log_channel:
            return _CreateCaseResult(
                successful = False,
                case       = None,
            )

        data = CASE_MAP[type(payload)]

        view = LayoutView()
        container = Container[view](TextDisplay(f"# {data.title}"), color = data.color)

        # ⸻ Add the target information.

        if isinstance(payload, LockdownAddPayload | LockdownRemovePayload):
            pass
        elif isinstance(payload, PurgePayload):
            if payload.target is not None:
                target = payload.target
                target_table = {
                    "Target"    : target.mention,
                    "Name"      : target.name,
                    "Target ID" : target.id,
                }
                target_info  = (
                    "## Target\n"
                   f"{format_table(target_table)}"
                )

                container.add_item(VisibleLargeSeparator())
                if target.guild_avatar:
                    container.add_item(ThumbnailSection(target_info, thumbnail = Thumbnail[view](target.guild_avatar.url)))
                else:
                    container.add_text(target_info)
        else:
            target = payload.target
            target_table = {
                "Target"    : target.mention,
                "Name"      : target.name,
                "Target ID" : target.id,
            }
            target_info  = (
                "## Target\n"
               f"{format_table(target_table)}"
            )

            container.add_item(VisibleLargeSeparator())
            if target.guild_avatar:
                container.add_item(ThumbnailSection(target_info, thumbnail = Thumbnail[view](target.guild_avatar.url)))
            else:
                container.add_text(target_info)

        # ⸻ Add the moderator information.

        moderator = payload.moderator
        moderator_table = {
            "Moderator"      : moderator.mention,
            "Moderator Name" : moderator.name,
            "Moderator ID"   : moderator.id,
        }
        moderator_info  = (
            "## Moderator\n"
           f"{format_table(moderator_table)}"
        )

        container.add_item(VisibleLargeSeparator())
        if moderator.guild_avatar:
            container.add_item(ThumbnailSection(moderator_info, thumbnail = Thumbnail[view](moderator.guild_avatar.url)))
        else:
            container.add_text(moderator_info)

        # ⸻ Case details.

        details : dict[str, object] = {}

        if isinstance(payload, BanAddPayload):
            details["Message Delete History"] = f"{payload.seconds_to_delete} seconds"
        elif isinstance(payload, TimeoutAddPayload):
            details["Duration"] = f"{payload.length} seconds"
        elif isinstance(payload, LockdownAddPayload | LockdownRemovePayload):
            details["Channel"] = payload.channel.mention
        elif isinstance(payload, PurgePayload):
            details["Channel"] = payload.channel.mention
            details["Amount"]  = payload.amount
            details["Forced"]  = payload.force

        if isinstance(
            payload,
            BanAddPayload
            | QuarantineAddPayload
            | KickPayload
            | TimeoutAddPayload
            | BanRemovePayload
            | QuarantineRemovePayload
            | TimeoutRemovePayload,
        ):
            details["DM Sent"] = payload.dm_user

        # ⸻ Add the case details.

        if details:
            container.add_items(
                VisibleLargeSeparator(),
                TextDisplay(
                    "## Details\n"
                   f"{format_table(details)}",
                ),
            )

        # ⸻ Add the reason.

        container.add_items(
            VisibleLargeSeparator(),
            TextDisplay(
                "## Reason\n"
               f"{payload.reason}",
            ),
        )

        # ⸻ Add the current time.

        container.add_items(
            VisibleLargeSeparator(),
            TextDisplay(f"-# {format_now()} | {format_now("R")}"),
        )

        view.add_item(container)

        # ⸻ Save the case into the database.

        action_type = type(payload).__name__.replace("Payload", "").lower()
        moderator_id = payload.moderator.id
        reason = payload.reason

        target_id = payload.target.id if not isinstance(payload, LockdownAddPayload | LockdownRemovePayload) and payload.target is not None else None
        channel_id = payload.channel.id if isinstance(payload, PurgePayload | LockdownAddPayload | LockdownRemovePayload) else None

        dm_user           = None
        seconds_to_delete = None
        timeout_length    = None
        purge_amount      = None
        purge_force       = None
        related_case_id   = None

        if isinstance(payload, BanAddPayload):
            dm_user = int(payload.dm_user)
            seconds_to_delete = payload.seconds_to_delete
        elif isinstance(payload, TimeoutAddPayload):
            dm_user = int(payload.dm_user)
            timeout_length = payload.length
        elif isinstance(payload, QuarantineAddPayload | KickPayload | BanRemovePayload | TimeoutRemovePayload | QuarantineRemovePayload):
            dm_user = int(payload.dm_user)
        elif isinstance(payload, PurgePayload):
            purge_amount = payload.amount
            purge_force  = int(payload.force)

        try:
            if action_type.endswith("remove") and (target_id is not None or channel_id is not None):
                corresponding = action_type.replace("remove", "add")
                if target_id is not None:
                    async with self.bot.db.execute(
                        t"SELECT id FROM Cases WHERE target_id = {target_id} AND action_type = {corresponding} AND expired = 0 ORDER BY id DESC LIMIT 1",
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row is not None:
                            related_case_id = cast("int", row[0])
                elif channel_id is not None:
                    async with self.bot.db.execute(
                        t"SELECT id FROM Cases WHERE channel_id = {channel_id} AND action_type = {corresponding} AND expired = 0 ORDER BY id DESC LIMIT 1",
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row is not None:
                            related_case_id = cast("int", row[0])

            cursor = await self.bot.db.execute(
                t"INSERT INTO Cases ("
                t"    action_type, moderator_id, target_id, reason, "
                t"    dm_user, seconds_to_delete, timeout_length, channel_id, purge_amount, purge_force, related_case_id"
                t") VALUES ("
                t"    {action_type}, {moderator_id}, {target_id}, {reason}, "
                t"    {dm_user}, {seconds_to_delete}, {timeout_length}, {channel_id}, {purge_amount}, {purge_force}, {related_case_id}"
                t")",
            )
            new_case_id = cursor.lastrowid

            if not new_case_id:
                return _CreateCaseResult(
                    successful = False,
                    case       = None,
                )

            await self.bot.db.execute(
                t"UPDATE Cases SET expired = 1, related_case_id = {new_case_id} WHERE id = {related_case_id}",
            )
            await self.bot.db.commit()
        except Exception:
            self._log_failure("case database insertion")
            return _CreateCaseResult(
                successful = False,
                case       = None,
            )
        else:
            successful = True

        # ⸻ Log the case.

        try:
            await log_channel.send(
                view             = view,
                allowed_mentions = AllowedMentions.none(),
            )
        except Forbidden:
            return _CreateCaseResult(
                successful = False,
                case       = None,
            )
        except HTTPException:
            self._log_failure("case logging")
            return _CreateCaseResult(
                successful = successful,
                case       = None,
            )

        return _CreateCaseResult(
            successful = successful,
            case       = Case(
                id                = new_case_id,
                action_type       = action_type,
                moderator         = payload.moderator,
                target            = payload.target if not isinstance(payload, LockdownAddPayload | LockdownRemovePayload) and isinstance(payload.target, Member) else None,
                reason            = reason,
                channel           = payload.channel if isinstance(payload, PurgePayload | LockdownAddPayload | LockdownRemovePayload) else None,
                created_at        = datetime.now(UTC),
                dm_user           = bool(dm_user) if dm_user is not None else None,
                seconds_to_delete = seconds_to_delete,
                timeout_length    = timeout_length,
                purge_amount      = purge_amount,
                purge_force       = bool(purge_force) if purge_force is not None else None,
                expired           = False,
                related_case_id   = related_case_id,
            ),
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_case
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_case(self, case_id : int, /) -> Case | None:
        """
        Get a case from the database by its ID.

        Parameters
        ----------
        case_id : `int`
            The ID of the case to get.
        /

        Returns
        -------
        `Case | None`
            The case if found, otherwise None.
        """
        try:
            async with self.bot.db.execute(t"SELECT * FROM Cases WHERE id = {case_id}") as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
        except Exception:
            self._log_failure(f"fetching case {case_id}")
            return None

        moderator_id = cast("int", row["moderator_id"])
        target_id    = cast("int | None", row["target_id"])

        moderator = self.guild.get_member(moderator_id) or await self.guild.fetch_member(moderator_id)
        target    = self.guild.get_member(target_id)    or await self.guild.fetch_member(target_id) if target_id else None

        channel_id = cast("int | None", row["channel_id"])
        channel    = self.guild.get_channel(channel_id) or await self.guild.fetch_channel(channel_id) if channel_id else None

        created_at = cast("str | datetime", row["created_at"])
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        return Case(
            id                = cast("int", row["id"]),
            action_type       = cast("str", row["action_type"]),
            moderator         = moderator,
            target            = target,
            reason            = cast("str", row["reason"]),
            channel           = channel if isinstance(channel, GuildMessagable) else None,
            created_at        = created_at,
            dm_user           = bool(cast("int | None", row["dm_user"])),
            seconds_to_delete = cast("int | None", row["seconds_to_delete"]),
            timeout_length    = cast("int | None", row["timeout_length"]),
            purge_amount      = cast("int | None", row["purge_amount"]),
            purge_force       = bool(cast("int | None", row["purge_force"])),
            expired           = bool(cast("int", row["expired"])),
            related_case_id   = cast("int | None", row["related_case_id"]),
        )
