from difflib import SequenceMatcher
from operator import itemgetter
from typing import Self, cast, final, override

from discord import SelectOption
from discord.app_commands import Command

from bot import Interaction
from bot.ui import (
    ActionRow,
    Button,
    ButtonSection,
    Container,
    Item,
    LayoutView,
    Modal,
    Select,
    TextDisplay,
    TextInput,
    VisibleLargeSeparator,
)
from constants import (
    COMMAND_EMOJI,
    CONTESTED_EMOJI,
    DEVELOPER_EMOJI,
    EMOJI_EMOJI,
    FINESTPERFECTIONISM_ID,
    HORIZONTAL_SETTINGS,
    MEMBER_EMOJI,
    MODERATION_EMOJI,
    PENCIL_EMOJI,
    QUERY_EMOJI,
    SEARCH_EMOJI,
    STANDSTILL_EMOJI,
    TEXT_EMOJI,
)
from core.exceptions import send_bad_operation, send_bad_request
from core.help import (
    AnnotatedCommand,
    Argument,
    get_help_metadata,
)
from core.paginator import UnnamedPaginator
from core.utilities import format_command

type CommandList = list[AnnotatedCommand]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /help Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def _build_sections(cmds : CommandList) -> list[str | Item[LayoutView]]:
    mention_strings = [
        format_command(cmd.qualified_name)
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

    scored = [
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

def _format_parameter(argument : Argument) -> str:
    prefix = "(Optional) " if argument.type.optional else ""

    if argument.type.type == "Choice":
        options  = ", ".join(argument.type.choices)
        arg_type = f"Choice[{options}]"
    else:
        arg_type = argument.type.type

    return f"`{argument.name} | {prefix}{arg_type}:` {argument.description}"


def _build_info_items(cmd : AnnotatedCommand) -> list[Item[LayoutView]]:
    metadata = get_help_metadata(cmd)

    items : list[Item[LayoutView]] = [
        TextDisplay(
            (
                f"# {format_command(cmd.qualified_name)} Command\n"
                f"*{cmd.description or "*No description provided.*"}*"
            ),
        ),
    ]

    if metadata.arguments:
        items.extend(
            [
                VisibleLargeSeparator(),
                TextDisplay("## Arguments"),
                *(
                    TextDisplay(_format_parameter(argument))
                    for argument in metadata.arguments.values()
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
    text_input : TextInput[Self] = TextInput(label = "Enter a command name.")

    def __init__(self, cmds : CommandList) -> None:
        super().__init__()
        self._commands = cmds

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        query   = self.text_input.value
        matches = _fuzzy_search(query, self._commands)

        # ⸻ No commands matched closely enough to the query...

        if not matches:
            await send_bad_request(
                interaction,
                title    =  "query commands",
                subtitle = f'No commands found matching "{query}".',
            )
            return

        paginator = UnnamedPaginator(
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
class _InfoButton(Button[UnnamedPaginator]):
    def __init__(self, cmd : AnnotatedCommand) -> None:
        self._command = cmd
        super().__init__(emoji = SEARCH_EMOJI)

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_message(view = _InfoView(self._command), ephemeral = True)

@final
class _CategorySelect(Select[UnnamedPaginator]):
    def __init__(self, cmds : CommandList) -> None:
        self._commands = cmds

        super().__init__(
            placeholder = "Select a command category.",
            options     = [
                SelectOption(
                    label       = "All Commands",
                    value       = "all",
                    description = "All bot commands.",
                    emoji       = HORIZONTAL_SETTINGS,
                    default     = True,
                ),
                SelectOption(
                    label       = "Moderation Commands",
                    value       = "moderation",
                    description = "Moderation commands. Numerous children.",
                    emoji       = MODERATION_EMOJI,
                ),
                SelectOption(
                    label       = "Server Commands",
                    value       = "server",
                    description = "Server commands. Children: configure, health, info",
                    emoji       = EMOJI_EMOJI,
                ),
                SelectOption(
                    label       = "Role Commands",
                    value       = "role",
                    description = "Role commands. Children: compare, duplicate, info, members, permissions",
                    emoji       = PENCIL_EMOJI,
                ),
                SelectOption(
                    label       = "Channel Commands",
                    value       = "channel",
                    description = "Channel commands. Children: compare, duplicate, info, permissions, sync",
                    emoji       = TEXT_EMOJI,
                ),
                SelectOption(
                    label       = "Member Commands",
                    value       = "member",
                    description = "Member commands. Children: info",
                    emoji       = MEMBER_EMOJI,
                ),
            ],
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        value = self.values[0]

        # ⸻ Filter the title and commands based on the select input

        match value:
            case "moderation":
                filtered = [c for c in self._commands if c.qualified_name.startswith("moderation")]
                title    = f"# {MODERATION_EMOJI} Moderation Commands"
            case "server":
                filtered = [c for c in self._commands if c.qualified_name.startswith("server")]
                title    = f"# {EMOJI_EMOJI} Server Commands"
            case "role":
                filtered = [c for c in self._commands if c.qualified_name.startswith("role")]
                title    = f"# {PENCIL_EMOJI} Role Commands"
            case "channel":
                filtered = [c for c in self._commands if c.qualified_name.startswith("channel")]
                title    = f"# {TEXT_EMOJI} Channel Commands"
            case "member":
                filtered = [c for c in self._commands if c.qualified_name.startswith("member")]
                title    = f"# {MEMBER_EMOJI} Member Commands"
            case _:
                filtered = self._commands
                title    = f"# {HORIZONTAL_SETTINGS} All Commands"

        for option in self.options:
            option.default = (option.value == value)

        paginator = cast("UnnamedPaginator", self.view)
        paginator.update_data(title, _build_sections(filtered))

        await interaction.response.edit_message(view = paginator)

@final
class _QueryButton(Button[UnnamedPaginator]):
    def __init__(self, cmds : CommandList) -> None:
        self._commands = cmds
        super().__init__(emoji = QUERY_EMOJI)

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_modal(_QueryModal(self._commands))

async def run_help(interaction : Interaction, name : str | None = None) -> None:
    await interaction.response.defer(ephemeral = True)

    # ⸻ Grab the commands from the cache and then sort them.

    cmds = [
        c for c in interaction.client.get_commands_cache()
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

        view = UnnamedPaginator(
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
                        "I am not quite sure who I will serve for right now... but hopefully that will change!\n"
                       f"## {DEVELOPER_EMOJI} My Developer\n"
                       f"My developer is <@{FINESTPERFECTIONISM_ID}>. I was created and am actively maintained by him.\n"
                       f"## {STANDSTILL_EMOJI} What I Do\n"
                        "- **Advanced UI:** I utilize Components V2, modals, and views, to provide a clean user interface that is both easy to navigate and visually appealing.\n"
                        "- **Guild Information:** I have a system to automatically manage guild information, such as rules, partnerships, and more.\n"
                        "- **Informational Commands:** I have utilites for server information, member information, and more for staff members and the public.\n"
                       f"## {CONTESTED_EMOJI} Issues?\n"
                       f"Should you have feedback or any issues with me, please speak to my developer."
                    ),
                ),
            ),
        )

        # ⸻ and then send it

        await interaction.followup.send(view = view, ephemeral = True)
