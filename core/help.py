from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from discord.app_commands import Command, Group
from discord.ext import commands

if TYPE_CHECKING:
    from collections.abc import Callable

type AnnotatedCommand = Command[Group | commands.Cog, ..., object]
type _ArgumentTypes = Literal[
    "Attachment",
    "Boolean",
    "String",
    "Integer",
    "Float",
    "Mentionable",
    "Channel",
    "Role",
    "User",
    "Choice",
    "Autocomplete",
]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@dataclass(frozen = True, slots = True)
class ArgumentType:
    type     : _ArgumentTypes
    choices  : list[str]
    optional : bool

    def __post_init__(self) -> None:
        if self.choices and self.type != "Choice":
            error = f"Expected type = Choice if using choices, not '{self.type}'"
            raise ValueError(error)


@dataclass(frozen = True, slots = True)
class Argument:
    name        : str
    type        : ArgumentType
    description : str


@dataclass(frozen = True, slots = True)
class HelpMetadata:
    arguments : dict[str, Argument] = field(default_factory = dict)


_registry : dict[object, HelpMetadata] = {}

def help_description[GroupT : Group | commands.Cog, **P, T](
    *,
    arguments : dict[str, Argument],
) -> Callable[[Command[GroupT, P, T]], Command[GroupT, P, T]]:
    metadata = HelpMetadata(arguments = arguments)

    def decorator(cmd : Command[GroupT, P, T]) -> Command[GroupT, P, T]:
        _registry[cmd] = metadata
        return cmd

    return decorator

def get_help_metadata[GroupT : Group | commands.Cog, **P, T](cmd : Command[GroupT, P, T]) -> HelpMetadata:
    return _registry.get(cmd, HelpMetadata())
