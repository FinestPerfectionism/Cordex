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
    """
    Represents a command restriction.

    Parameters
    ----------
    user_ids : `frozenset[int]`
        The IDs of the users allowed to use the command.
    role_ids : `frozenset[int]`
        The IDs of the roles allowed to use the command.
    """

    user_ids : frozenset[int]
    role_ids : frozenset[int]

    def allows(self, member : Member) -> bool:
        """
        Check if a member is allowed to use a command.

        Parameters
        ----------
        member : `Member`
            The member to check.

        Returns
        -------
        `bool`
            Whether the member is allowed to use the command or not.
        """
        if member.id in self.user_ids:
            return True

        return any(role.id in self.role_ids for role in member.roles)


def is_restrictable[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> bool:
    """
    Check if a command is able to be restricted.

    Parameters
    ----------
    command : `Command[GroupT, P, T] | Group`
        The command to check.
    /

    Returns
    -------
    `bool`
        Whether the command is able to be restricted or not.
    """
    if isinstance(command, Group):
        return False

    parts = command.qualified_name.split()
    if parts and parts[0] in _UNRESTRICTABLE_ROOTS:
        return False

    return not command.extras.get("unrestrictable", False)


def requires_restriction[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T], /) -> Command[GroupT, P, T]:
    """
    Mark a command as requiring restriction.

    Parameters
    ----------
    command : `Command[GroupT, P, T]`
        The command to mark.
    /

    Returns
    -------
    `Command[GroupT, P, T]`
        The restricted command.
    """
    command.extras["requires_restriction"] = True
    return command


def is_restriction_required[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> bool:
    """
    Check if a command requires restriction.

    Parameters
    ----------
    command : `Command[GroupT, P, T] | Group`
        The command to check.
    /

    Returns
    -------
    `bool`
        Whether the command requires restriction or not.
    """
    if type(command) is Group:
        return False

    return command.extras.get("requires_restriction", False) is True
