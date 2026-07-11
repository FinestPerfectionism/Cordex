from typing import TYPE_CHECKING, override

from discord.ui import Button

from bot.ui import blurple

from ._base import InfoSupportSection

if TYPE_CHECKING:
    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Ticket Support Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TicketButton(Button["TicketComponents"]):
    def __init__(self) -> None:
        super().__init__(label = "Open Ticket", style = blurple)

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
