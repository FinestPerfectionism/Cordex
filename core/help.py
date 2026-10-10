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


def command_help[GroupT : Group | commands.Cog, **P, T](
    *,
    description : str | None = None,
    parameters  : dict[str, str] | None = None,
) -> Callable[[Command[GroupT, P, T]], Command[GroupT, P, T]]:
    def decorator(command : Command[GroupT, P, T], /) -> Command[GroupT, P, T]:
        setattr(command, "__help_description__", description or command.description)

        for parameter in command.parameters:
            help_name        = parameter.name
            help_description = parameter.description

            if (
                parameters is not None and
                parameter.name in parameters and
                not isinstance(value := parameters[parameter.name], type)
            ):
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
        description = getattr(command, "__help_description__", command.description),
        parameters  = [
            HelpParameter(
                name         = getattr(parameter, "__help_name__", parameter.display_name),
                description  = getattr(parameter, "__help_description__", parameter.description),
                required     = parameter.required,
                type         = parameter.type,
                choices      = parameter.choices,
                autocomplete = parameter.autocomplete,
            ) for parameter in command.parameters
        ],
    )
