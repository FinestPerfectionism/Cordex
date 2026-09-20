from collections.abc import Callable
from dataclasses import dataclass
from inspect import isclass
from typing import cast, final, overload

from discord import Member
from discord.app_commands import Command, Group
from discord.ext import commands

from bot.types import AnnotatedCommand

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


@overload
def unrestrictable[T : type](target : T, /) -> T: ...


@overload
def unrestrictable[T : AnnotatedCommand | Group | Callable[..., object]](target : T, /) -> T: ...


def unrestrictable(target : object, /) -> object:
    if isclass(target):
        cls_target = target
        for attr_name in dir(cls_target):
            if attr_name.startswith("__"):
                continue

            attr = cast("object", getattr(cls_target, attr_name))

            if isinstance(attr, Group):
                attr.extras[_UNRESTRICTABLE_KEY] = True

            elif (
                isinstance(attr, Command)
                or hasattr(attr, "__discord_app_commands_unwrap__")
                or hasattr(attr, "__commands_extras__")
            ) or isinstance(attr, Callable):
                unrestrictable(cast("Callable[..., object]", attr))

        return cls_target

    unwrapped = cast("object", getattr(target, "__discord_app_commands_unwrap__", target) or target)

    if isinstance(unwrapped, Command | Group):
        unwrapped.extras[_UNRESTRICTABLE_KEY] = True
    else:
        for attr_str in ("__commands_extras__", "__discord_app_commands_extras__"):
            if not hasattr(target, attr_str):
                setattr(target, attr_str, cast("dict[str, bool]", {}))
            cast("dict[str, bool]", getattr(target, attr_str))[_UNRESTRICTABLE_KEY] = True

    return target


def is_restrictable[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> bool:
    if isinstance(command, Group):
        return False

    parts = command.qualified_name.split()
    if parts and parts[0] in _UNRESTRICTABLE_ROOTS:
        return False

    return not cast("bool", command.extras.get(_UNRESTRICTABLE_KEY, False))
