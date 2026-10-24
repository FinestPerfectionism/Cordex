
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from discord import AppCommandOptionType
from discord.app_commands import Choice, Command, Group
from discord.ext.commands import Cog

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help State
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@dataclass(slots = True, kw_only = True)
class HelpParameter:
    """Represents the mock-parameter of a command, replicated to that of `discord.app_commands.Parameter`, except with support for non-display help descriptions."""

    name         : str
    description  : str
    required     : bool
    type         : AppCommandOptionType
    choices      : list[Choice[int | float | str]]
    autocomplete : bool


@dataclass(slots = True, kw_only = True)
class HelpCommand:
    """Represents a mock-command, replicated to that of `discord.app_commands.Command`, except with support for non-display help descriptions."""

    name        : str
    description : str
    parameters  : list[HelpParameter]


def command_help[GroupT : Group | Cog, **P, T](
    *,
    description : str            | None = None,
    parameters  : dict[str, str] | None = None,
) -> Callable[[Command[GroupT, P, T]], Command[GroupT, P, T]]:
    """
    Get help information for a command and it's parameters.

    Parameters
    ----------
    *
    description : `str | None = None`
        The description to set for the command.
    parameters : `dict[str, str] | None = None`
        The description to set for the parameters of command, with the key representing the parameter's name and the value representing the help description.

    Returns
    -------
    `Callable[[Command[GroupT, P, T]], Command[GroupT, P, T]]`
        The decorator applying these changes.
    """
    def decorator(command : Command[GroupT, P, T], /) -> Command[GroupT, P, T]:
        command.extras["__help_description__"] = description or command.description

        parameter_overrides : dict[str, str] = {}
        if parameters is not None:
            parameter_overrides.update(
                {
                    name : parameter_description for name, parameter_description in parameters.items()
                    if not isinstance(parameter_description, type)
                },
            )

        command.extras["__help_parameters__"] = parameter_overrides
        return command

    return decorator


def get_command_help[GroupT : Group | Cog, **P, T](command : Command[GroupT, P, T] | Group, /) -> HelpCommand:
    """
    Get help information for a command.

    Parameters
    ----------
    command : `Command[GroupT, P, T] | Group`
        The command to get help information for.
    /

    Returns
    -------
    `HelpCommand`
        The mock-command with help information.

    Raises
    ------
    TypeError
        The command is an instance of `Group`.
    """
    if isinstance(command, Group):
        raise TypeError

    extras              = command.extras
    command_description = cast("str", extras.get("__help_description__", command.description))
    parameter_overrides = cast("dict[str, str]", extras.get("__help_parameters__", {}))

    help_parameters : list[HelpParameter] = []
    for parameter in command.parameters:
        fallback_description = parameter.description or ""
        parameter_description = parameter_overrides.get(parameter.name, fallback_description)

        help_parameters.append(
            HelpParameter(
                name         = parameter.display_name,
                description  = parameter_description,
                required     = parameter.required,
                type         = parameter.type,
                choices      = parameter.choices,
                autocomplete = parameter.autocomplete,
            ),
        )

    return HelpCommand(
        name        = command.qualified_name,
        description = command_description,
        parameters  = help_parameters,
    )
