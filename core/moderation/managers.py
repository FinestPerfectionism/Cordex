from asyncio import Semaphore, gather
from typing import Literal, final

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
    # get_quarantined_members
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def get_quarantined_members(self) -> list[Member] | None:
        ...

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # quarantine_enforce
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    type EnforceTypes = Literal["Channel", "Role"]

    async def quarantine_enforce(self, enforce_type : EnforceTypes) -> None:
        quarantine_role = await self.bot.config(self.guild).get_moderation_quarantine_role()
        if not quarantine_role:
            return

        if enforce_type == "Channel":
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
                            reason    = "Scheduled quarantine enforce.",
                        )
                    except Forbidden:
                        pass
                    except HTTPException:
                        self._log_failure("channel quarantine enforcement")

            await gather(*(edit_channel(channel) for channel in self.guild.channels))

        if enforce_type == "Role":
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

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Note Manager
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class NoteManager:
    def __init__(self, bot : Cordex, guild : Guild) -> None:
        super().__init__()
        self.bot   = bot
        self.guild = guild
