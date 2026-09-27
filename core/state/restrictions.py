from dataclasses import dataclass
from typing import final

from discord import Member
from discord.app_commands import Command, Group
from discord.ext import commands

_UNRESTRICTABLE_ROOTS = frozenset({"bot-owner", "about"})

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Restriction State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
@dataclass(frozen = True, slots = True)
class Restriction:
    user_ids : frozenset[int]
    role_ids : frozenset[int]

    def allows(self, member : Member) -> bool:
        if member.id in self.user_ids:
            return True

        return any(role.id in self.role_ids for role in member.roles)


# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Unrestrictable Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def is_restrictable[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> bool:  # codespell:ignore
    if isinstance(command, Group):
        return False

    parts = command.qualified_name.split()
    if parts and parts[0] in _UNRESTRICTABLE_ROOTS:
        return False

    return not command.extras.get("unrestrictable", False)


# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Required-Configuration Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def requires_configuration[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T], /) -> Command[GroupT, P, T]:
    command.extras["requires_configuration"] = True
    return command


def is_configuration_required[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> bool:
    if isinstance(command, Group):
        return False

    return bool(command.extras.get("requires_configuration", False))
