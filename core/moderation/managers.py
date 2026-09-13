from asyncio import Semaphore, gather
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

    def _log_failure(self, msg : str, /) -> None:
        log.exception("Failure during %s in guild %s, %s", msg, self.guild.name, self.guild.id)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_channels
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_channels(self) -> list[GuildChannel] | None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # enforce
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def enforce(self) -> None:
        semaphore = Semaphore(5)

        async def edit_channel(_channel : GuildChannel) -> None:
            async with semaphore:
                try:
                    # await channel.set_permissions(
                    #     ...,
                    #     overwrite = ...,
                    #     reason    = "Lockdown enforce.",
                    # )
                    ...
                except Forbidden:
                    pass
                except HTTPException:
                    self._log_failure("channel quarantine enforcement")

        await gather(*(edit_channel(channel) for channel in self.guild.channels))

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

    def _log_failure(self, msg : str, /) -> None:
        log.exception("Failure during %s in guild %s, %s", msg, self.guild.name, self.guild.id)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # get_members
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_members(self) -> set[Member] | None:
        async with self.bot.db.execute(
            t"SELECT member_id FROM Quarantines WHERE guild_id = {self.guild.id}",
        ) as cursor:
            rows = await cursor.fetchall()
            if not rows:
                return None

        members : set[Member] = set()
        for row in rows:
            member_id = cast("int", row[0])
            member    = self.guild.get_member(member_id)
            if member:
                members.add(member)

        return members

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # enforce
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    type EnforceTypes = Literal["Channel", "Role", "Members"]

    async def enforce(self, enforce_type : EnforceTypes) -> None:
        config = self.bot.config(self.guild)

        quarantine_role = await config.get_moderation_quarantine_role()
        if not quarantine_role:
            return

        if enforce_type == "Channel":
            wants_enforcement = await config.get_moderation_quarantine_enforce_channels()
            if not wants_enforcement:
                return

            me = self.guild.me
            if not me or not me.guild_permissions.manage_channels:
                return

            semaphore = Semaphore(5)

            async def edit_channel(channel : GuildChannel) -> None:
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
                            reason    = "Quarantine enforce.",
                        )
                    except Forbidden:
                        pass
                    except HTTPException:
                        self._log_failure("channel quarantine enforcement")

            await gather(*(edit_channel(channel) for channel in self.guild.channels))

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
                except HTTPException:
                    self._log_failure("role quarantine enforcement")

        if enforce_type == "Members":
            me = self.guild.me
            if not me or not me.guild_permissions.manage_roles:
                return

            true_quarantined                   = await self.get_members()
            expected_quarantined : set[Member] = true_quarantined or set()
            role_quarantined                   = set(quarantine_role.members)

            if role_quarantined == expected_quarantined:
                return

            semaphore = Semaphore(5)

            async def remove_role(member : Member) -> None:
                async with semaphore:
                    try:
                        await member.remove_roles(quarantine_role, reason = "Quarantine enforce.")
                    except Forbidden:
                        pass
                    except HTTPException:
                        self._log_failure("member quarantine removal")

            async def add_role(member : Member) -> None:
                async with semaphore:
                    try:
                        await member.add_roles(quarantine_role, reason = "Quarantine enforce.")
                    except Forbidden:
                        pass
                    except HTTPException:
                        self._log_failure("member quarantine addition")

            await gather(
                *(remove_role(member) for member in (role_quarantined - expected_quarantined)),
                *(add_role(member)    for member in (expected_quarantined - role_quarantined)),
            )
