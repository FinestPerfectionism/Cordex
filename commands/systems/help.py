from difflib import SequenceMatcher
from operator import itemgetter
from typing import cast, final, override

from discord import SelectOption
from discord.app_commands import Command, command, describe
from discord.ext import commands
from discord.ui import ActionRow, Button, Item, Modal, Select, TextDisplay, TextInput

from bot import Cordex, Interaction, bot
from bot.ui import ButtonSection, Container, LayoutView, VisibleLargeSeparator
from constants import (
    BOT_OWNER_ID,
    COMMAND_EMOJI,
    EMOJI_EMOJI,
    HORIZONTAL_SETTINGS,
    MODERATION_EMOJI,
    QUERY_EMOJI,
    SEARCH_EMOJI,
)
from core.exceptions import send_bad_operation, send_bad_request
from core.help import (
    AnnotatedCommand,
    get_help_metadata,
    help_description,
    label_for_parameter,
)
from core.paginator import Paginator
from core.utilities import format_command

type CommandList = list[AnnotatedCommand]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Help Command
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def _build_sections(cmds : CommandList) -> list[str | Item[LayoutView]]:
    mention_strings = [
        format_command(bot, cmd.qualified_name)
        for cmd in cmds
    ]

    return [
        ButtonSection(
            f"**{n}.** {m_str}\n-# {cmd.description or "*No description provided.*"}",
            button = _InfoButton(cmd),
        )
        for n, (cmd, m_str) in enumerate(zip(cmds, mention_strings, strict = False), start = 1)
    ]

def _fuzzy_search(query : str, cmds : CommandList) -> CommandList:
    query_lower = query.strip().lower()

    scored : list[tuple[float, AnnotatedCommand]] = [
        (
            SequenceMatcher(
                None,
                query_lower,
                cmd.qualified_name.lower(),
            ).ratio(),
            cmd,
        )
        for cmd in cmds
    ]

    for index, (score, cmd) in enumerate(scored):
        if query_lower and query_lower in cmd.qualified_name.lower():
            scored[index] = (max(score, 0.85), cmd)

    scored.sort(key = itemgetter(0), reverse = True)

    return [cmd for score, cmd in scored if score >= 0.4]

def _build_info_items(cmd : AnnotatedCommand) -> list[Item[LayoutView]]:
    metadata = get_help_metadata(cmd)
    summary  = metadata.summary or cmd.description or "*No description provided.*"

    items : list[Item[LayoutView]] = [
        TextDisplay(
            (
                f"# {format_command(bot, cmd.qualified_name)} Command\n"
                f"*{summary}*"
            ),
        ),
    ]

    if cmd.parameters:
        items.extend(
            [
                VisibleLargeSeparator(),
                TextDisplay("## Arguments"),
                *(
                    TextDisplay(f"`{param.name} | {label_for_parameter(param)}:` {metadata.arguments.get(param.name, param.description) or '*No description provided.*'}")
                    for param in cmd.parameters
                ),
            ],
        )

    return items

@final
class _InfoView(LayoutView):
    def __init__(self, cmd : AnnotatedCommand) -> None:
        super().__init__()
        self.add_item(Container(*_build_info_items(cmd)))

@final
class _QueryModal(Modal, title = "Query"):
    text_input : TextInput[LayoutView] = TextInput(label = "Enter a command name.")

    def __init__(self, cmds : CommandList) -> None:
        super().__init__()
        self._commands = cmds

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        query   = self.text_input.value
        matches = _fuzzy_search(query, self._commands)

        # ⸻ No commands matched closely enough to the query...

        if not matches:
            return await send_bad_request(
                interaction,
                title    =  "query commands",
                subtitle = f'No commands found matching "{query}".',
            )

        paginator = Paginator(
            f"# {SEARCH_EMOJI} Search Results",
            _build_sections(matches),
            data_name = "Commands",
            per_page  = 10,
            container = True,
        )

        try:
            await interaction.response.send_message(view = paginator, ephemeral = True)

        # ⸻ Unhandled error.

        except Exception:
            await send_bad_operation(interaction, title = "query commands")
            raise

@final
class _InfoButton(Button[Paginator]):
    def __init__(self, cmd : AnnotatedCommand) -> None:
        self._command = cmd
        super().__init__(emoji = SEARCH_EMOJI)

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_message(view = _InfoView(self._command), ephemeral = True)

@final
class _CategorySelect(Select[Paginator]):
    def __init__(self, cmds : CommandList) -> None:
        self._commands = cmds

        super().__init__(
            placeholder = "Select a command category.",
            options     = [
                SelectOption(
                    label       = "All Commands",
                    value       = "all",
                    description = "All bot commands. Children: moderation, server, bot-owner, help",
                    emoji       = HORIZONTAL_SETTINGS,
                    default     = True,
                ),
                SelectOption(
                    label       = "Moderation Commands",
                    value       = "moderation",
                    description = "Moderation commands. Children: ban, lockdown, note, quarantine, timeout, tickets, kick, purge",
                    emoji       = MODERATION_EMOJI,
                ),
                SelectOption(
                    label       = "Server Commands",
                    value       = "server",
                    description = "Server commands. Children: channel, member, partnership, role, configure, info",
                    emoji       = EMOJI_EMOJI,
                ),
            ],
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        value = self.values[0]

        if value == "moderation":
            filtered = [c for c in self._commands if c.qualified_name.startswith("moderation")]
            title    = f"# {MODERATION_EMOJI} Moderation Commands"
        elif value == "server":
            filtered = [c for c in self._commands if c.qualified_name.startswith("server")]
            title    = f"# {EMOJI_EMOJI} Server Commands"
        else:
            filtered = self._commands
            title    = f"# {HORIZONTAL_SETTINGS} All Commands"

        for option in self.options:
            option.default = (option.value == value)

        paginator = cast(Paginator, self.view)
        paginator.update_data(title, _build_sections(filtered))

        await interaction.response.edit_message(view = paginator)

@final
class _QueryButton(Button[Paginator]):
    def __init__(self, cmds : CommandList) -> None:
        self._commands = cmds
        super().__init__(emoji = QUERY_EMOJI)

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_modal(_QueryModal(self._commands))

@final
class HelpCommand(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        self.bot = bot

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /help Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @help_description(arguments = {"name" : "The name of the command to view information for."})
    @command(
        name        = "help",
        description = "Provides assistance into a command. Defaults to information about the bot and a list of commands.",
    )
    @describe(name = "The name of the command to view information for.")
    async def cmd_help(self, interaction : Interaction, name : str | None = None) -> None:
        await interaction.response.defer(ephemeral = True)

        # ⸻ Grab the commands from the cache and then sort them.

        cmds = [
            c for c in bot.get_commands_cache()
            if isinstance(c, Command)
            and not c.qualified_name.startswith("bot-owner")
        ]
        cmds.sort(key = lambda c : c.qualified_name)

        if name:
            matches = _fuzzy_search(name, cmds)

            # ⸻ No commands matched closely enough to the query...

            if not matches:
                await send_bad_request(interaction, subtitle = f'No commands found matching "{name}".')
                return

            await interaction.followup.send(view = _InfoView(matches[0]), ephemeral = True)
        else:
            sections = _build_sections(cmds)

            # ⸻ Build the view,

            view = Paginator(
                f"# {HORIZONTAL_SETTINGS} All Commands",
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
                        button = _QueryButton(cmds),
                    ),
                    ActionRow(_CategorySelect(cmds)),
                ),
            )
            view.add_below(
                Container(
                    TextDisplay(
                        (
                            "# About me,\n"
                            "I am a bot designed exclusively to serve the server *goobers*. You won't see me anywhere else! (probably)\n"
                            "## My Developer\n"
                           f"My developer is <@{BOT_OWNER_ID}>. I was created and am actively maintained by him.\n"
                            "## What I Do\n"
                            "- **Advanced Moderation:** Staff can moderate multiple users at once with advanced logging, appeals, and state. I also have a ticket system for user support.\n"
                            "- **Guild Information:** I have a system to automatically manage guild information, such as rules, partnerships, and more.\n"
                            "- **Informational Commands:** I have utilites for server information, member information, and more for staff members and the public.\n"
                            "## Issues?\n"
                           f"Should you have feedback or any issues with me, please speak to my developer."
                        ),
                    ),
                ),
            )

            # ⸻ and then send it

            await interaction.followup.send(view = view, ephemeral = True)

async def setup(bot : Cordex) -> None:
    cog = HelpCommand(bot)
    await bot.add_cog(cog)
