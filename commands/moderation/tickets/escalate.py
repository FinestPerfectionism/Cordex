from discord import Thread

from bot import Interaction, bot
from constants import DIRECTORS_ROLE_ID, MODERATORS_ROLE_ID, TICKETS_CHANNEL_ID
from core.exceptions import send_bad_environment_channel, send_bad_request
from core.responses import format_send
from core.state import get_ticket, set_ticket_team

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation tickets escalate Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_tickets_escalate(interaction : Interaction) -> None:
    channel = interaction.channel

    # ⸻ Ensure that the command is being run in a thread of tickets.

    if not isinstance(channel, Thread) or not channel.parent or channel.parent.id != TICKETS_CHANNEL_ID:
        await send_bad_environment_channel(interaction)
        return

    # ⸻ Ensure this is an open moderator ticket that hasn't already been escalated.

    ticket = await get_ticket(bot.db, thread_id = channel.id)

    if ticket is None or ticket["team"] != "moderator":
        await send_bad_request(interaction, subtitle = "This ticket cannot be escalated to the director team.")
        return

    guild = channel.guild

    # ⸻ Kick every moderator out of the thread.

    members = await channel.fetch_members()

    for thread_member in members:
        member = guild.get_member(thread_member.id)

        if member is None:
            continue

        if any(role.id == MODERATORS_ROLE_ID for role in member.roles):
            await channel.remove_user(member)

    # ⸻ Rename the thread and flip its team internally

    new_name = channel.name.replace("Moderator Ticket", "Director Ticket", 1)

    await channel.edit(name = new_name)
    await set_ticket_team(bot.db, thread_id = channel.id, team = "director")

    # ⸻ Success!

    await format_send(
        interaction,
        msg_type  = "success",
        title     = "escalated ticket",
        subtitle  = "This ticket has been escalated to directors.",
        ephemeral = False,
    )
    await channel.send(f"<@&{DIRECTORS_ROLE_ID}>")
