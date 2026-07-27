from typing import override

from discord.ui import Button

from bot import Interaction
from bot.ui import blurple

from ._base import InfoSupportSection

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Leave Support Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class LeaveButton(Button["LeaveComponents"]):
    def __init__(self) -> None:
        super().__init__(label = "Open Leave Ticket", style = blurple, custom_id = "persistent:leave_button")

    @override
    async def callback(self, interaction : Interaction) -> None:
        await interaction.response.send_message(
            "This button does nothing right now. :[",
            ephemeral = True,
        )

class LeaveComponents(InfoSupportSection):
    def __init__(self) -> None:
        super().__init__(
            title       = "Leave",
            description = "Leave tickets for staff",
            text        = (
                "When you plan to be unavailable for a period of time, you must notify directors using this channel. This system exists solely to track staff availability and ensure operational coverage. Taking leave is expected and acceptable, provided it is communicated properly.\n\n"
                "When submitting a leave request, include the following information:\n\n"
                "- **Beginning Date:** The exact date your leave will begin.\n"
                "   - **Note:** If you will be going on leave effective immediately, do __not__ provide a beginning date.\n"
                "- **Ending Date:** The exact date your leave will end.\n"
                "   - **Note:** If you do not know when you will return, do __not__ provide an ending date.\n"
                "- **Timer:** A timer for your leave (incompatible with ending date).\n"
                "- **Reason:** A reason for your leave (optional).\n\n"
                "## Types of Leave\n\n"
                "- **Standard:** Places you on personal leave while retaining your staff roles. This is used when you are temporarily unavailable but will resume normal duties after your leave ends.\n"
                "- **Clean:** Temporarily removes all staff roles while you are on leave. Your roles will automatically be restored when your leave ends"
            ),
            note        = "If you do not have the personal leave role, you are expected to be online and active",
            footer      = (
                "We look forward to assisting you! Sincerely,\n"
                "-# The Goobers Moderation team"
            ),
            button      = LeaveButton(),
        )
