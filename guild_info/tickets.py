from typing import TYPE_CHECKING, Self, cast, override

from discord import ChannelType, Member, SelectOption, TextChannel
from discord.ui import Button, Label, Modal, Select

from bot.ui import blurple
from constants import (
    DIRECTOR_EMOJI,
    DIRECTORS_ROLE_ID,
    MODERATOR_EMOJI,
    MODERATORS_ROLE_ID,
    STAFF_ROLE_ID,
)
from core.responses import format_send
from core.state import save_ticket

from ._base import InfoSupportSection

if TYPE_CHECKING:
    from bot import Cordex, Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Ticket Support Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class TicketModal(Modal, title = "Open Ticket"):
    def __init__(self) -> None:
        super().__init__(timeout = None)

        self.select : Select[Self] = Select(
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
                    default     = True,
                ),
            ],
        )

        self.add_item(
            Label(
                text        = "Team",
                description = "Select which staff team to contact.",
                component   = self.select,
            ),
        )

    @override
    async def on_submit(self, interaction : "Interaction") -> None:
        await interaction.response.defer(ephemeral = True)

        channel = interaction.channel
        choice  = self.select.values[0]

        mapping : dict[str, tuple[str, str, str]] = {
            "director"  : ("Director Ticket",  f"<@&{DIRECTORS_ROLE_ID}>",  "Director"),
            "moderator" : ("Moderator Ticket", f"<@&{MODERATORS_ROLE_ID}>", "Moderator"),
        }
        ticket_type, team_mention, team_name = mapping[choice]

        if isinstance(channel, TextChannel):
            client = cast("Cordex", interaction.client)

            # ⸻ Create thread and add the ticket opener

            ticket = await channel.create_thread(
                name      = f"{ticket_type} — {interaction.user.name}",
                type      = ChannelType.private_thread,
                invitable = False,
            )

            await ticket.add_user(interaction.user)

            # ⸻ Persist ticket state

            await save_ticket(client.db, thread_id = ticket.id, team = choice)
            await format_send(
                interaction,
                msg_type  = "success",
                title     = "created ticket",
                subtitle  = f"{team_name} ticket created: {ticket.mention}",
                ephemeral = True,
            )
            await ticket.send(team_mention)

class TicketButton(Button["TicketComponents"]):
    def __init__(self) -> None:
        super().__init__(label = "Open Ticket", style = blurple, custom_id = "persistent:ticket_button")

    @override
    async def callback(self, interaction : "Interaction") -> None:

        # ⸻ We know that the button will run in a guild but the type checker doesn't...

        if not isinstance(interaction.user, Member):
            return

        user_roles = {role.id for role in interaction.user.roles}

        # ⸻ Directors may not open tickets.

        if DIRECTORS_ROLE_ID in user_roles:
            await format_send(
                interaction,
                msg_type  = "error",
                title     = "open ticket",
                subtitle  = "Directors cannot open support tickets. Contact other directors for issues.",
                ephemeral = True,
            )
            return

        # ⸻ Staff may only open Director tickets.

        if STAFF_ROLE_ID in user_roles:
            await interaction.response.defer(ephemeral = True)

            channel = interaction.channel
            if isinstance(channel, TextChannel):
                client = cast("Cordex", interaction.client)

                # ⸻ Create thread and add the staff member

                ticket = await channel.create_thread(
                    name      = f"Director Ticket — {interaction.user.name}",
                    type      = ChannelType.private_thread,
                    invitable = False,
                )

                await ticket.add_user(interaction.user)

                # ⸻ Persist ticket state

                await save_ticket(client.db, thread_id = ticket.id, team = "director")
                await format_send(
                    interaction,
                    msg_type  =  "success",
                    title     =  "created ticket",
                    subtitle  = f"Director ticket created: {ticket.mention}",
                    ephemeral = True,
                )
                await ticket.send(f"<@&{DIRECTORS_ROLE_ID}>")
            return

        # ⸻ Members users may open any ticket.

        await interaction.response.send_modal(TicketModal())

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
