# ruff: file-ignore[set-attr-with-constant]

from collections.abc import Callable
from dataclasses import dataclass

from discord import AppCommandOptionType
from discord.app_commands import Choice, Command, Group
from discord.ext import commands

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@dataclass(slots = True, kw_only = True)
class HelpParameter:
    name         : str
    description  : str
    required     : bool
    type         : AppCommandOptionType
    choices      : list[Choice[int | float | str]]
    autocomplete : bool


@dataclass(slots = True, kw_only = True)
class HelpCommand:
    name        : str
    description : str
    parameters  : list[HelpParameter]


class Existing:
    """Allows a command parameter's description to remain unedited."""

    def __new__(cls):
        error = "Existing cannot be instantiated"
        raise TypeError(error)


@dataclass(frozen = True)
class Rename:
    existing : str
    new      : str


def command_help[GroupT : Group | commands.Cog, **P, T](
    *,
    description : str | None = None,
    parameters  : dict[str | Rename, str | type[Existing]] | None = None,
) -> Callable[[Command[GroupT, P, T]], Command[GroupT, P, T]]:
    def decorator(command : Command[GroupT, P, T], /) -> Command[GroupT, P, T]:
        setattr(command, "__help_description__", description or command.description)

        lookup : dict[str, tuple[str, str | type[Existing]]] = {}
        if parameters is not None:
            for key, value in parameters.items():
                if isinstance(key, Rename):
                    lookup[key.existing] = (key.new, value)
                else:
                    lookup[key] = (key, value)

        for parameter in command.parameters:
            help_name        = parameter.name
            help_description = parameter.description

            if parameters is not None and parameter.name in lookup:
                new_name, value = lookup[parameter.name]
                help_name       = new_name
                if not isinstance(value, type):
                    help_description = value

            setattr(parameter, "__help_name__", help_name)
            setattr(parameter, "__help_description__", help_description)

        return command

    return decorator


def get_command_help[GroupT : Group | commands.Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> HelpCommand | None:
    if isinstance(command, Group):
        return None

    return HelpCommand(
        name        = command.qualified_name,
        description = getattr(command, "__help_description__", None) or command.description,
        parameters  = [
            HelpParameter(
                name         = getattr(parameter, "__help_name__", parameter.name),
                description  = getattr(parameter, "__help_description__", parameter.description),
                required     = parameter.required,
                type         = parameter.type,
                choices      = parameter.choices,
                autocomplete = parameter.autocomplete,
            ) for parameter in command.parameters
        ],
    )
