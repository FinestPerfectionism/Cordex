from collections.abc import Callable
from dataclasses import dataclass, field

from discord import AppCommandOptionType
from discord.app_commands import Command, Group, Parameter
from discord.ext import commands

type AnnotatedCommand = Command[Group | commands.Cog, ..., object]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@dataclass(frozen = True, slots = True)
class HelpMetadata:
    summary   : str | None     = None
    arguments : dict[str, str] = field(default_factory = dict)


_TYPE_LABELS : dict[AppCommandOptionType, str] = {
    AppCommandOptionType.string      : "Text Input",
    AppCommandOptionType.integer     : "Number",
    AppCommandOptionType.boolean     : "Yes/No",
    AppCommandOptionType.user        : "User",
    AppCommandOptionType.channel     : "Channel",
    AppCommandOptionType.role        : "Role",
    AppCommandOptionType.mentionable : "Mentionable",
    AppCommandOptionType.number      : "Decimal",
    AppCommandOptionType.attachment  : "Attachment",
}

_registry : dict[str, HelpMetadata] = {}

def help_description[GroupT : Group | commands.Cog, **P, T](
    *,
    summary   : str            | None = None,
    arguments : dict[str, str] | None = None,
) -> Callable[[Command[GroupT, P, T]], Command[GroupT, P, T]]:
    metadata = HelpMetadata(summary = summary, arguments = arguments or {})

    def decorator(cmd : Command[GroupT, P, T]) -> Command[GroupT, P, T]:
        _registry[cmd.qualified_name] = metadata
        return cmd

    return decorator

def get_help_metadata[GroupT : Group | commands.Cog, **P, T](cmd : Command[GroupT, P, T]) -> HelpMetadata:
    return _registry.get(cmd.qualified_name, HelpMetadata())

def label_for_parameter(param : Parameter) -> str:
    if param.choices:
        return "Choice"

    return _TYPE_LABELS.get(param.type, "Text Input")
