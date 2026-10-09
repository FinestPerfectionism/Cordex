from typing import final

from discord import AppCommandOptionType
from discord.utils import get as utils_get

from bot import Interaction
from bot.ui import Container, LayoutView, TextDisplay, VisibleLargeSeparator
from constants import REQUIRED_EMOJI
from core.exceptions import send_bad_argument
from core.help import HelpCommand, HelpParameter, get_command_help

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /help Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def _build_parameter_sections(parameters : list[HelpParameter]) -> str:
    option_types = {
        AppCommandOptionType.subcommand       : "",
        AppCommandOptionType.subcommand_group : "",
        AppCommandOptionType.string           : "Text Input",
        AppCommandOptionType.integer          : "Integer",
        AppCommandOptionType.boolean          : "Boolean",
        AppCommandOptionType.user             : "User",
        AppCommandOptionType.channel          : "Channel",
        AppCommandOptionType.role             : "Role",
        AppCommandOptionType.mentionable      : "Role or User",
        AppCommandOptionType.number           : "Number",
        AppCommandOptionType.attachment       : "Attachment",
    }
    return "\n\n".join(
        (
            f"**{parameter.name}{f" {REQUIRED_EMOJI}" if parameter.required else ""}**\n"
            f"-# {option_types[parameter.type]} | *{parameter.description}*"
        ) for parameter in parameters
    )


@final
class HelpView(LayoutView):
    def __init__(self, command : HelpCommand) -> None:
        super().__init__()
        self.add_item(
            Container(
                TextDisplay(
                    f"# /{command.name}\n"
                    f"-# *{command.description}*",
                ),
                VisibleLargeSeparator(),
                TextDisplay(_build_parameter_sections(command.parameters)),
            ),
        )


async def run_help(interaction : Interaction, command_name : str) -> None:
    command = utils_get(interaction.client.tree.walk_commands(), qualified_name = command_name)
    if not command:
        await send_bad_argument(
            interaction,
            subtitle = {"command" : "Command not found."},
        )
        return

    details = get_command_help(command)
    if not details:
        return

    await interaction.response.send_message(view = HelpView(details))
