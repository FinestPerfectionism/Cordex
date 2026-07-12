from typing import TYPE_CHECKING, override

from discord import SelectOption
from discord.ui import Button, Label, Modal, Select

from bot.ui import blurple
from constants import DIRECTOR_EMOJI, MODERATOR_EMOJI

from ._base import InfoSupportSection

if TYPE_CHECKING:
    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Ticket Support Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TicketModal(Modal, title = "Open Ticket"):
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.add_item(
            Label(
                text        = "Team",
                description = "Select which staff team to contact.",
                component   = Select(
                    placeholder = "Which team would you like to contact?",
                    options     = [
                        SelectOption(
                            label       = "Contact Directors",
                            value       = "director",
                            emoji       = DIRECTOR_EMOJI,
                            description = "Contact directors for partnerships or moderation concerns about staff legitimacy.",
                        ),
                        SelectOption(
                            label       = "Contact Moderators",
                            value       = "moderator",
                            emoji       = MODERATOR_EMOJI,
                            description = "Contact moderators for questions or moderation concerns about everyday users.",
                        ),
                    ],
                ),
            ),
        )

    @override
    async def on_submit(self, interaction : "Interaction") -> None:
        ...

class TicketButton(Button["TicketComponents"]):
    def __init__(self) -> None:
        super().__init__(label = "Open Ticket", style = blurple, custom_id = "persistent:ticket_button")

    @override
    async def callback(self, interaction : "Interaction") -> None:
        await interaction.response.send_message(
            "This button does nothing right now. :[",
            ephemeral = True,
        )

class TicketComponents(InfoSupportSection):
    def __init__(self) -> None:
        super().__init__(
            title       = "Tickets",
            description = "Support tickets for moderation",
            text        = (
                "Tickets are used to contact the moderation team for support, reports, or questions that cannot be handled publicly.\n\n"
                "- **How to Start:** Open the correct ticket category and clearly explain your issue from the start.\n"
                "- **Be Specific:** Provide usernames, IDs, timestamps, or screenshots if applicable.\n"
                "- **Respect Moderators:** Remain calm and respectful at all times.\n\n"
                "Tickets are handled in the order they are received, and response times may vary"
            ),
            note        = "You may run `/tickets close` to close your ticket",
            footer      = (
                "We look forward to assisting you! Sincerely,\n"
                "-# The Goobers Moderation team"
            ),
            button      = TicketButton(),
        )
