from asyncio import Semaphore
from typing import Literal, cast, final

from discord import Forbidden, Guild, HTTPException, Member
from discord.abc import GuildChannel

from bot import Cordex, log

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Managers
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Lockdown Manager
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class LockdownManager:
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
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # enforce
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def enforce(self) -> None:
        semaphore = Semaphore(5)

        for _channel in self.guild.channels:
            async with semaphore:
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

    type EnforceTypes = Literal["Channel", "Role", "Members"]

    async def enforce(self, enforce_type : EnforceTypes) -> None:
        config = self.bot.config(self.guild)

        quarantine_role = await config.get_moderation_quarantine_role()
        if not quarantine_role:
            return

        # ⸻ Channel

        if enforce_type == "Channel":

            # ⸻

            wants_enforcement = await config.get_moderation_quarantine_enforce_channels()
            if not wants_enforcement:
                return

            me = self.guild.me
            if not me or not me.guild_permissions.manage_channels:
                return

            semaphore = Semaphore(5)

            for channel in self.guild.channels:
                async with semaphore:
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

            semaphore = Semaphore(5)

            # ⸻ Some role members have the quarantine role but are not quarantined. Remove the role.

            for member in (role_quarantined - expected_quarantined):
                async with semaphore:
                    try:
                        await member.remove_roles(quarantine_role, reason = "Quarantine enforcement.")
                    except Forbidden:
                        pass
                    except HTTPException as e:
                        rate_limited = e.status == 429
                        self._log_failure("member quarantine removal", rate_limited = rate_limited)
                        if rate_limited:
                            raise

            # ⸻ Some quarantined members are missing the quarantine role. Add the role.

            for member in (expected_quarantined - role_quarantined):
                async with semaphore:
                    try:
                        await member.add_roles(quarantine_role, reason = "Quarantine enforcement.")
                    except Forbidden:
                        pass
                    except HTTPException as e:
                        rate_limited = e.status == 429
                        self._log_failure("member quarantine addition", rate_limited = rate_limited)
                        if rate_limited:
                            raise
