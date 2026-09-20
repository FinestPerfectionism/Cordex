from dataclasses import dataclass
from typing import cast, final

from discord import Member
from discord.app_commands import Command, Group
from discord.ext import commands

_UNRESTRICTABLE_KEY   = "unrestrictable"
_UNRESTRICTABLE_ROOTS = frozenset({"bot-owner"})

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


def unrestrictable[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T], /) -> Command[GroupT, P, T]:
    command.extras[_UNRESTRICTABLE_KEY] = True
    return command


def is_restrictable[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> bool:
    if isinstance(command, Group):
        return False

    if command.qualified_name.split()[0] in _UNRESTRICTABLE_ROOTS:
        return False

    return not cast("bool", command.extras.get(_UNRESTRICTABLE_KEY, False))
