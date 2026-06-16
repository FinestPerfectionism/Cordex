from discord.app_commands import command as app_command
from discord.ext import commands
from discord.ui import ActionRow, Button, Container, LayoutView, TextDisplay, button

from bot import Cordex, Interaction
from core.permissions import director_cmd
from core.utilities import VisibleLargeSeparator, red

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Configuration Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class PickerRow(ActionRow["ConfigurationView"]):
    def __init__(self) -> None:
        super().__init__()

    @button(label = "Antinuke", style = red)
    async def btn_antinuke(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        _ = await interaction.response.send_message(
            "This button does nothing right now. :[",
            ephemeral = True,
        )

    @button(label = "Moderation", style = red)
    async def btn_moderation(self, interaction : Interaction, _button : Button[LayoutView]) -> None:
        _ = await interaction.response.send_message(
            "This button does nothing right now. :[",
            ephemeral = True,
        )

class ConfigurationView(LayoutView):
    def __init__(self) -> None:
        super().__init__()
        _ = self.add_item(
            Container(
                TextDisplay("# Configuration"),
                VisibleLargeSeparator(),
                PickerRow(),
            ),
        )

class ConfigurationCommands(
    commands.Cog,
    name        = "configuration",
    description = "Directors only — Configuration command.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    @app_command(
        name        = "configure",
        description = "Configure guild settings.",
    )
    @director_cmd()
    async def cmd_configure(self, interaction : Interaction) -> None:
        _ = await interaction.response.send_message(
            view      = ConfigurationView(),
            ephemeral = True,
        )

async def setup(bot : Cordex) -> None:
    cog = ConfigurationCommands(bot)
    await bot.add_cog(cog)
