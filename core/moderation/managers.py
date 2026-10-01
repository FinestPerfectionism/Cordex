from typing import TYPE_CHECKING, Literal, cast, final

from discord import Forbidden, Guild, HTTPException, Member, Permissions
from discord.abc import GuildChannel

if TYPE_CHECKING:
    from bot import Cordex

from ._base import log

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Managers
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Lockdown Manager
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class LockdownManager:
    """
    A manager for lockdown operations that don't pertain to primary moderation actions.

    Parameters
    ----------
    bot : `Cordex`
        The bot instance.
    guild : `Guild`
        The guild where lockdown is being managed.
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
    # get_channels
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_channels(self) -> set[GuildChannel]:
        """
        Fetch every channel in lockdown found in the database.

        Returns
        -------
        `set[GuildChannel]`
            Every channel in lockdown found in the database.
        """
        async with self.bot.db.execute(
            t"SELECT channel_id FROM Lockdowns WHERE guild_id = {self.guild.id}",
        ) as cursor:
            rows = await cursor.fetchall()
            if not rows:
                return set()

        return {
            channel for row in rows
            if (channel := self.guild.get_channel(cast("int", row[0])))
        }

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # enforce
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def enforce(self) -> None:
        """
        Enforces quarantine operations by ensuring channels in lockdown have the proper permission overwrites.

        Raises
        ------
        HTTPException
            The enforcement caused a ratelimit.
        """
        for _channel in self.guild.channels:
            try:
                # await channel.set_permissions(
                #     ...,
                #     overwrite = ...,
                #     reason    = "Lockdown enforcement.",
                # )
                ...
            except Forbidden:
                pass
            except HTTPException as e:
                rate_limited = e.status == 429
                self._log_failure("channel lockdown enforcement", rate_limited = rate_limited)
                if rate_limited:
                    raise

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Quarantine Manager
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class QuarantineManager:
    """
    A manager for quarantine operations that don't pertain to primary moderation actions.

    Parameters
    ----------
    bot : `Cordex`
        The bot instance.
    guild : `Guild`
        The guild where quarantine is being managed.
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
    # get_members
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_members(self) -> set[Member]:
        """
        Fetch every quarantined member found in the database.

        Returns
        -------
        `set[Member]`
            Every quarantined member found in the database.
        """
        async with self.bot.db.execute(
            t"SELECT member_id FROM Quarantines WHERE guild_id = {self.guild.id}",
        ) as cursor:
            rows = await cursor.fetchall()
            if not rows:
                return set()

        return {
            member for row in rows
            if (member := self.guild.get_member(cast("int", row[0])))
        }

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # enforce
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    type EnforceTypes = Literal["Channels", "Role", "Members"]

    async def enforce(self, enforce_type : EnforceTypes) -> None:
        """
        Enforces quarantine operations.

        - Channels: Ensures the quarantine role has certain permissions disabled in every guild channel.quarantine channel enforcement.
        - Role: Ensures the quarantine role has all permissions set to false and that the role is below the bot's top role.
        - Members: Ensures the quarantine role doesn't contain members that are not quarantined, and that quarantined members have the quarantine role.

        The channels and role types will have no effect if the guild has not configured quarantine enforcement for those types. The members type will always run as it is not configurable (always enabled).

        Parameters
        ----------
        enforce_type : `Literal["Channels", "Role", "Members"]`
            The type of quarantine enforcement to execute.

        Raises
        ------
        HTTPException
            The enforcement caused a ratelimit.
        """
        config = self.bot.config(self.guild)

        quarantine_role = await config.get_moderation_quarantine_role()
        if not quarantine_role:
            return

        # ⸻ Channels

        if enforce_type == "Channels":
            wants_enforcement = await config.get_moderation_quarantine_enforce_channels()
            if not wants_enforcement:
                return

            me = self.guild.me
            if not me or not me.guild_permissions.manage_channels:
                return

            for channel in self.guild.channels:
                overwrites = channel.overwrites_for(quarantine_role)

                overwrites.update(
                    send_messages_in_threads = False,
                    create_instant_invite    = False,
                    send_messages            = False,
                    create_public_threads    = False,
                    create_private_threads   = False,
                    read_messages            = False,
                )

                try:
                    await channel.set_permissions(
                        quarantine_role,
                        overwrite = overwrites,
                        reason    = "Quarantine enforcement.",
                    )
                except Forbidden:
                    pass
                except HTTPException as e:
                    rate_limited = e.status == 429
                    self._log_failure("channel quarantine enforcement", rate_limited = rate_limited)
                    if rate_limited:
                        raise

        # ⸻ Role

        if enforce_type == "Role":
            wants_enforcement = await config.get_moderation_quarantine_enforce_roles()
            if not wants_enforcement:
                return

            me = self.guild.me
            if not me or not me.guild_permissions.manage_roles:
                return

            my_role = me.top_role
            if quarantine_role.permissions.value != 0:
                try:
                    await quarantine_role.edit(permissions = Permissions.none())
                except Forbidden:
                    pass
                except HTTPException as e:
                    rate_limited = e.status == 429
                    self._log_failure("role quarantine enforcement", rate_limited = rate_limited)
                    if rate_limited:
                        raise

            if my_role.position > 1 and quarantine_role.position != my_role.position - 1:
                try:
                    await quarantine_role.edit(position = my_role.position - 1)
                except Forbidden:
                    pass
                except HTTPException as e:
                    rate_limited = e.status == 429
                    self._log_failure("role quarantine enforcement", rate_limited = rate_limited)
                    if rate_limited:
                        raise

        # ⸻ Members

        if enforce_type == "Members":
            me = self.guild.me
            if not me or not me.guild_permissions.manage_roles:
                return

            true_quarantined     = await self.get_members()
            expected_quarantined = true_quarantined or set()
            role_quarantined     = set(quarantine_role.members)

            # ⸻ Role members matches quarantined members. Exit.

            if role_quarantined == expected_quarantined:
                return

            # ⸻ Some role members have the quarantine role but are not quarantined. Remove the role.

            for member in (role_quarantined - expected_quarantined):
                try:
                    await member.remove_roles(quarantine_role, reason = "Quarantine enforcement.")
                except Forbidden:
                    pass
                except HTTPException as e:
                    rate_limited = e.status == 429
                    self._log_failure("member quarantine enforcement (removal)", rate_limited = rate_limited)
                    if rate_limited:
                        raise

            # ⸻ Some quarantined members are missing the quarantine role. Add the role.

            for member in (expected_quarantined - role_quarantined):
                try:
                    await member.add_roles(quarantine_role, reason = "Quarantine enforcement.")
                except Forbidden:
                    pass
                except HTTPException as e:
                    rate_limited = e.status == 429
                    self._log_failure("member quarantine enforcement (addition)", rate_limited = rate_limited)
                    if rate_limited:
                        raise
