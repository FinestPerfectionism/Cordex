from difflib import SequenceMatcher
from operator import itemgetter
from typing import Self, final, override

from discord import SelectOption
from discord.app_commands import Command, Group
from discord.ext import commands

from bot import Interaction
from bot.ui import (
    ActionRow,
    Button,
    ButtonSection,
    Container,
    Item,
    Label,
    LayoutView,
    MentionableSelect,
    Modal,
    Select,
    TextDisplay,
    TextInput,
)
from constants import (
    COMMAND_EMOJI,
    EMOJI_EMOJI,
    HORIZONTAL_SETTINGS,
    MEMBER_EMOJI,
    MEMBERS_EMOJI,
    MODERATION_EMOJI,
    PENCIL_EMOJI,
    QUERY_EMOJI,
    SEARCH_EMOJI,
    TEXT_EMOJI,
)
from core.exceptions import send_bad_argument, send_bad_operation, send_bad_request
from core.paginator import UnnamedPaginator
from core.utilities import format_command

type AnnotatedCommand = Command[Group | commands.Cog, ..., object]
type CommandList = list[AnnotatedCommand]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server commands Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def _build_sections(commands : CommandList) -> list[str | Item[LayoutView]]:
    mentions = [
        format_command(command.qualified_name)
        for command in commands
    ]

    return [
        ButtonSection(
            f"**{i}.** {mention}\n"
            f"-# {command.description or "*No description provided.*"}",
            button = _ConfigButton(command),
        )
        for i, (command, mention) in enumerate(zip(commands, mentions, strict = False), start = 1)
    ]

def _fuzzy_search(query : str, commands : CommandList) -> CommandList:
    query_lower = query.strip().lower()

    scored = [
        (
            SequenceMatcher(
                None,
                query_lower,
                command.qualified_name.lower(),
            ).ratio(),
            command,
        ) for command in commands
    ]

    for index, (score, command) in enumerate(scored):
        if query_lower and query_lower in command.qualified_name.lower():
            scored[index] = (max(score, 0.85), command)

    scored.sort(key = itemgetter(0), reverse = True)

    return [cmd for score, cmd in scored if score >= 0.4]

@final
class _QueryModal(Modal, title = "Query"):
    def __init__(self, commands : CommandList) -> None:
        super().__init__()
        self._commands = commands

        self._text_input = TextInput[Self](placeholder = "Enter a query...")
        self.text_input  = Label[Self](
            text        = "Query",
            description = "The query to enter.",
            component   = self._text_input,
        )

        self.add_item(self.text_input)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        query   = self._text_input.value
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
class _ConfigModal(Modal):
    def __init__(self, command : AnnotatedCommand) -> None:
        super().__init__(title = f"Configuring {command.qualified_name}")

        self.current_allowed = TextDisplay[Self]("...")

        self._allowed = MentionableSelect[Self](placeholder = "Enter up to 25 users/roles...", max_values = 25)
        self.allowed  = Label[Self](
            text        = "Allowed",
            description = "The users/roles allowed to run the command. Uses OR logic.",
            component   = self._allowed,
        )

        self.add_items(self.current_allowed, self.allowed)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        allowed = self._allowed.values

        guild = interaction.guild
        if not guild:
            return

        quarantine_role = interaction.client.config(guild).get_moderation_quarantine_role()
        if quarantine_role in allowed:
            await send_bad_argument(
                interaction,
                subtitle = {"allowed" : "Quarantine role cannot be used as a user/role command restriction."},
            )

@final
class _ConfigButton(Button[UnnamedPaginator]):
    def __init__(self, command : AnnotatedCommand) -> None:
        self._command = command
        super().__init__(emoji = PENCIL_EMOJI)

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_modal(_ConfigModal(self._command))

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
                    description = "Server commands. Children: commands, configure, health, info",
                    emoji       = EMOJI_EMOJI,
                ),
                SelectOption(
                    label       = "Role Commands",
                    value       = "role",
                    description = "Role commands. Children: compare, duplicate, info, members, permissions",
                    emoji       = MEMBERS_EMOJI,
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

        if not self.view:
            return

        for option in self.options:
            option.default = (option.value == value)

        self.view.update_data(title, _build_sections(filtered))

        await interaction.response.edit_message(view = self.view)

@final
class _QueryButton(Button[UnnamedPaginator]):
    def __init__(self, cmds : CommandList) -> None:
        self._commands = cmds
        super().__init__(emoji = QUERY_EMOJI)

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_modal(_QueryModal(self._commands))

async def run_server_commands(interaction : Interaction) -> None:
    await interaction.response.defer()

    # ⸻ Grab the commands from the cache and then sort them.

    commands = [
        command for command in interaction.client.get_commands_cache()
        if isinstance(command, Command) and
        not command.qualified_name.startswith("bot-owner")
    ]
    commands.sort(key = lambda c : c.qualified_name)

    sections = _build_sections(commands)

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
               f"# {COMMAND_EMOJI} Command Browser\n"
                "-# Select a category to view commands.",
                button = _QueryButton(commands),
            ),
            ActionRow(_CategorySelect(commands)),
        ),
    )

    # ⸻ ...and then send it.

    await interaction.followup.send(view = view)
