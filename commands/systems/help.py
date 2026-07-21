from asyncio import gather
from typing import final, override

from discord import SelectOption
from discord.app_commands import Command, command, describe
from discord.ext import commands
from discord.ui import ActionRow, Button, Item, Modal, Select, TextDisplay, TextInput

from bot import Cordex, Interaction, bot
from bot.ui import ButtonSection, Container, LayoutView, blurple
from constants import (
    COMMAND_EMOJI,
    EMOJI_EMOJI,
    HORIZONTAL_SETTINGS,
    MODERATION_EMOJI,
    SEARCH_EMOJI,
)
from core.paginator import Paginator
from core.utilities import format_command

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _QueryModal(Modal, title = "Query"):
    text_input : TextInput[LayoutView] = TextInput(label = "Enter a command name.")

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        await interaction.response.send_message("This doesn't do anything!", ephemeral = True)

class _InfoButton(Button[Paginator]):
    def __init__(self) -> None:
        super().__init__(emoji = SEARCH_EMOJI)

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_message("This doesn't do anything!", ephemeral = True)

class _CategorySelect(Select[Paginator]):
    def __init__(self) -> None:
        super().__init__(
            placeholder = "Select a command category.",
            options     = [
                SelectOption(
                    label       = "All Commands",
                    description = "All bot commands. Children: moderation, server, bot-owner, help",
                    emoji       = HORIZONTAL_SETTINGS,
                ),
                SelectOption(
                    label       = "Moderation",
                    description = "Moderation commands. Children: ban, lockdown, note, quarantine, timeout, tickets, kick, purge",
                    emoji       = MODERATION_EMOJI,
                ),
                SelectOption(
                    label       = "Server",
                    description = "Server commands. Children: channel, member, partnership, role, configure, info",
                    emoji       = EMOJI_EMOJI,
                ),
            ],
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_message("This doesn't do anything!", ephemeral = True)

class _QueryButton(Button[Paginator]):
    def __init__(self) -> None:
        super().__init__(style = blurple, label = "Query")

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_modal(_QueryModal())

class HelpCommand(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot : Cordex = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /help Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(
        name        = "help",
        description = "Provides assistance into a command. Defaults to information about the bot and a list of commands.",
    )
    @describe(name = "The name of the command (or command group) to view information for.")
    async def cmd_help(self, interaction : Interaction, name : str | None = None) -> None:
        await interaction.response.defer(ephemeral = True)

        if name:
            await interaction.followup.send("`name` does nothing right now :[, but running the command with no argument works.")
        else:
            cmds = [c for c in bot.get_commands_cache() if isinstance(c, Command)]
            cmds.sort(key = lambda c : c.qualified_name)

            mention_strings = await gather(
               *[
                    format_command(bot, cmd.qualified_name)
                    for cmd in cmds
                ],
            )

            sections : list[str | Item[LayoutView]] = [
                ButtonSection(
                    f"**{n}.** {m_str}\n-# {cmd.description or "*No description provided.*"}",
                    button = _InfoButton(),
                )
                for n, (cmd, m_str) in enumerate(zip(cmds, mention_strings, strict = False), start = 1)
            ]

            view = Paginator(
                "# All Commands",
                sections,
                data_name = "Commands",
                container = True,
            )
            view.add_above(
                Container(
                    ButtonSection(
                        (
                           f"# {COMMAND_EMOJI} Command Browser\n"
                            "-# Select a category to view commands."
                        ),
                        button = _QueryButton(),
                    ),
                    ActionRow(_CategorySelect()),
                ),
            )
            view.add_below(
                Container(
                    TextDisplay(
                        (
                            "# About Cordex,\n"
                            ""
                        ),
                    ),
                ),
            )

            await interaction.followup.send(view = view)

async def setup(bot : Cordex) -> None:
    cog = HelpCommand(bot)
    await bot.add_cog(cog)
