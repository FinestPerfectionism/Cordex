from dataclasses import dataclass
from typing import final, overload

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


@overload
def requires_restriction[GroupT : Group | commands.Cog, **P, T](target : Command[GroupT, P, T], /) -> Command[GroupT, P, T]: ...

@overload
def requires_restriction[CogT : type[commands.GroupCog]](target : CogT, /) -> CogT: ...


def requires_restriction[
    GroupT : Group | commands.Cog, **P, T,
    CogT   : type[commands.GroupCog],
](target : Command[GroupT, P, T] | CogT, /) -> Command[GroupT, P, T] | CogT:
    """
    Mark a command or group of commands as requiring restriction.

    Parameters
    ----------
    target : `Command[GroupT, P, T] | GroupCog`
        The command or group of commands to mark as requiring restriction.
    /

    Returns
    -------
    `Command[GroupT, P, T] | GroupCog`
        The command or group of commands marked as restricted.
    """
    if not isinstance(target, Command):
        setattr(target, "__commands_extra_restriction__", True)  # ruff: ignore[set-attr-with-constant]
        return target

    target.extras["requires_restriction"] = True
    return target


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
