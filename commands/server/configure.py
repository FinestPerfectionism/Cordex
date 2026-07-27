from typing import Self, final

from discord import ChannelType
from discord.ui import (
    ActionRow,
    Button,
    ChannelSelect,
    TextDisplay,
    button,
    select,
)

from bot import Cordex, Interaction
from bot.ui import Container, LayoutView, VisibleLargeSeparator, blurple, red
from constants import ACCEPTED_EMOJI, COLOR_GREEN, COLOR_RED, COLOR_YELLOW, DENIED_EMOJI

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server configure Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class LoggingModerationRow(ActionRow["LoggingConfigurationView"]):
    def __init__(self) -> None:
        super().__init__()

    @select(
        cls           = ChannelSelect,
        placeholder   = "Choose a channel for Moderation logs...",
        channel_types = [
            ChannelType.text,
            ChannelType.private_thread,
            ChannelType.public_thread,
        ],
    )
    async def slct_logging_moderation(self, interaction : Interaction, select : ChannelSelect[LayoutView]) -> None:
        if not self.view:
            return

        channel = select.values[0]
        bot = interaction.client if isinstance(interaction.client, Cordex) else self.view.bot

        await bot.db.execute(
            """
            INSERT INTO GuildConfig (config_key, config_value)
            VALUES ('logging_moderation_channel', ?)
            ON CONFLICT(config_key) DO UPDATE SET config_value = excluded.config_value
            """,
            [str(channel.id)],
        )
        await bot.db.commit()

        await self.view.refresh()
        await interaction.response.edit_message(view = self.view)

class LoggingAntinukeRow(ActionRow["LoggingConfigurationView"]):
    def __init__(self) -> None:
        super().__init__()

    @select(
        cls           = ChannelSelect,
        placeholder   = "Choose a channel for Antinuke logs...",
        channel_types = [
            ChannelType.text,
            ChannelType.private_thread,
            ChannelType.public_thread,
        ],
    )
    async def slct_logging_antinuke(self, interaction : Interaction, select_item : ChannelSelect[LayoutView]) -> None:
        if not self.view:
            return

        channel = select_item.values[0]
        bot = interaction.client if isinstance(interaction.client, Cordex) else self.view.bot

        await bot.db.execute(
            """
            INSERT INTO GuildConfig (config_key, config_value)
            VALUES ('logging_antinuke_channel', ?)
            ON CONFLICT(config_key) DO UPDATE SET config_value = excluded.config_value
            """,
            [str(channel.id)],
        )
        await bot.db.commit()

        await self.view.refresh()
        await interaction.response.edit_message(view = self.view)

@final
class LoggingConfigurationView(LayoutView):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

        self.antinuke_display   : TextDisplay[Self] = TextDisplay("")
        self.moderation_display : TextDisplay[Self] = TextDisplay("")
        self.container          : Container         = Container(
            self.antinuke_display,
            LoggingAntinukeRow(),
            self.moderation_display,
            LoggingModerationRow(),
            color = COLOR_RED,
        )
        self.add_item(self.container)

    async def refresh(self) -> None:
        query = (
            "SELECT config_key, config_value FROM GuildConfig "
            "WHERE config_key IN ('logging_moderation_channel', 'logging_antinuke_channel')"
        )

        async with self.bot.db.execute(query) as cursor:
            rows = list(await cursor.fetchall())

        config_dict = {row[0] : row[1] for row in rows}
        configured_count = len(config_dict)

        if configured_count == 2:
            self.container.color = COLOR_GREEN
        elif configured_count == 1:
            self.container.color = COLOR_YELLOW
        else:
            self.container.color = COLOR_RED

        antinuke_id   = config_dict.get("logging_antinuke_channel")
        moderation_id = config_dict.get("logging_moderation_channel")

        antinuke_text = (
            f"{ACCEPTED_EMOJI} **Antinuke Logs Channel:**\n"
            f"Configured to <#{antinuke_id}>."
        ) if antinuke_id else (
           f"{DENIED_EMOJI} **Antinuke Logs Channel:**\n"
            "Not configured!"
        )

        moderation_text = (
            f"{ACCEPTED_EMOJI} **Moderation Logs Channel:**\n"
            f"Configured to <#{moderation_id}>."
        ) if moderation_id else (
           f"{DENIED_EMOJI} **Moderation Logs Channel:**\n"
            "Not configured!"
        )

        self.antinuke_display.content   = antinuke_text
        self.moderation_display.content = moderation_text

class PickerRow(ActionRow["ConfigurationView"]):
    def __init__(self) -> None:
        super().__init__()

    @button(label = "Antinuke", style = red)
    async def btn_antinuke(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await interaction.response.send_message(
            "This button does nothing right now. :[",
            ephemeral = True,
        )

    @button(label = "Moderation", style = red)
    async def btn_moderation(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        await interaction.response.send_message(
            "This button does nothing right now. :[",
            ephemeral = True,
        )

    @button(label = "Logging", style = blurple)
    async def btn_logging(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        if not self.view:
            return

        await interaction.response.defer(ephemeral = True)

        logging_view = LoggingConfigurationView(self.view.bot)
        await logging_view.refresh()

        await interaction.followup.send(
            view      = logging_view,
            ephemeral = True,
        )

@final
class ConfigurationView(LayoutView):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot
        self.add_item(
            Container(
                TextDisplay("# Guild Configuration"),
                VisibleLargeSeparator(),
                PickerRow(),
            ),
        )

async def run_server_configure(interaction : Interaction, bot : Cordex) -> None:
    await interaction.response.send_message(
        view      = ConfigurationView(bot = bot),
        ephemeral = True,
    )
