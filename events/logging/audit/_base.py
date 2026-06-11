import asyncio
import logging as log
from asyncio import Queue
from collections.abc import Iterable
from typing import TYPE_CHECKING

import discord
from discord import (
    Embed,
    Guild,
    Member,
    Object,
    PermissionOverwrite,
    Permissions,
    Role,
    TextChannel,
)
from discord.abc import Messageable
from discord.ext import commands, tasks
from typing_extensions import override

from constants import CHANGE_LOG_CHANNEL_ID

if TYPE_CHECKING:
    from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Audit Logging Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

SEND_INTERVAL = 1.0

class AuditQueue(commands.Cog):
    def __init__(self, bot : "Cordex") -> None:
        self.bot   : "Cordex"                         = bot
        self.queue : Queue[tuple[Messageable, Embed]] = Queue()
        _ = self.queue_worker.start()

    @override
    async def cog_unload(self) -> None:
        self.queue_worker.cancel()

    @tasks.loop(seconds = SEND_INTERVAL)
    async def queue_worker(self) -> None:
        if self.queue.empty():
            return

        channel, embed = await self.queue.get()
        try:
            _ = await channel.send(embed = embed)
        except discord.RateLimited as e:
            await asyncio.sleep(e.retry_after)
            await self.queue.put((channel, embed))
        except discord.HTTPException:
            log.exception("Failed to send log embed")
        finally:
            self.queue.task_done()

    @queue_worker.before_loop
    async def before_queue_worker(self) -> None:
        await self.bot.wait_until_ready()

    async def enqueue(self, channel : Messageable, embed : Embed) -> None:
        await self.queue.put((channel, embed))

class AuditCog(commands.Cog):
    def __init__(self, bot : "Cordex", queue : AuditQueue) -> None:
        self.bot            : "Cordex"     = bot
        self.log_channel_id : int          = CHANGE_LOG_CHANNEL_ID
        self._queue         : AuditQueue   = queue

    async def enqueue(self, channel : Messageable, embed : Embed) -> None:
        await self._queue.enqueue(channel, embed)

    async def get_log_channel(self, guild : Guild) -> TextChannel | None:
        channel = guild.get_channel(self.log_channel_id)
        if not isinstance(channel, TextChannel):
            log.warning("Logging channel %s not found in %s", self.log_channel_id, guild.name)
            return None
        return channel

    async def get_executor(
        self,
        guild       : Guild,
        action_type : discord.AuditLogAction,
        target_id   : int | None = None,
    ) -> Member | None:
        try:
            await asyncio.sleep(0.5)
            async for entry in guild.audit_logs(limit = 10, action = action_type):
                if (target_id is None or (entry.target is not None and entry.target.id == target_id)) and isinstance(entry.user, Member):
                    return entry.user
        except discord.HTTPException:
            log.exception("Error fetching audit log")
        return None

    def format_permissions(self, permissions : Permissions | Iterable[tuple[str, bool | None]]) -> str:
        if not permissions:
            return "None"

        perms : list[str] = []
        for perm, value in permissions:
            if value is not None:
                status    = "Allow" if value else "Deny"
                perm_name = perm.replace("_", " ").title()
                perms.append(f"{perm_name}: {status}")

        return "\n".join(perms) if perms else "None"

    type ChannelOverwrites = dict[Role | Member | Object, PermissionOverwrite]
    def get_overwrite_changes(self, before_overwrites : ChannelOverwrites, after_overwrites : ChannelOverwrites) -> list[str]:
        changes : list[str] = []
        all_targets         = set(before_overwrites.keys()) | set(after_overwrites.keys())

        for target in all_targets:
            before_ow = before_overwrites.get(target)
            after_ow  = after_overwrites.get(target)

            target_type = "Role" if isinstance(target, Role) else "Member"
            target_name = getattr(target, "name", str(target))
            target_id   = target.id if hasattr(target, "id") else "Unknown"

            match (before_ow, after_ow):
                case (None, after_ow) if after_ow is not None:
                    perms : list[str] = []
                    for perm, value in after_ow:
                        if value is not None:
                            status = "Allow" if value else "Deny"
                            perms.append(f"{perm.replace('_', ' ').title()}: {status}")
                    if perms:
                        changes.append(
                            f"**Added {target_type}** `{target_name}`\n`{target_id}`\n" + "\n".join(perms),
                        )

                case (_, None):
                    changes.append(f"**Removed {target_type}** `{target_name}`\n`{target_id}`")

                case _:
                    before_perms : dict[str, bool | None] = dict(before_ow) if before_ow is not None else {}
                    after_perms  : dict[str, bool | None] = dict(after_ow)

                    modified_perms : list[str] = []
                    for perm in set(before_perms.keys()) | set(after_perms.keys()):
                        before_val = before_perms.get(perm)
                        after_val  = after_perms.get(perm)

                        if before_val != after_val:
                            perm_name     = perm.replace("_", " ").title()
                            before_status = "Allow" if before_val else ("Deny" if before_val is False else "Neutral")
                            after_status  = "Allow" if after_val else ("Deny" if after_val is False else "Neutral")
                            modified_perms.append(f"{perm_name}: {before_status} → {after_status}")

                    if modified_perms:
                        changes.append(f"**Modified {target_type}** `{target_name}`\n`{target_id}`\n" + "\n".join(modified_perms))

        return changes
