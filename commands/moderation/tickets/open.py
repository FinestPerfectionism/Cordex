from discord import Thread

from bot import Interaction, bot
from constants import TICKETS_CHANNEL_ID
from core.exceptions import send_bad_environment_channel, send_bad_request
from core.responses import format_send
from core.state import set_ticket_state

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /moderation tickets open Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_mod_tickets_open(interaction : Interaction) -> None:
    channel = interaction.channel

    # ⸻ Ensure that the command is being run in a thread of tickets

    if not isinstance(channel, Thread) or not channel.parent or channel.parent.id != TICKETS_CHANNEL_ID:
        await send_bad_environment_channel(interaction)
        return

    # ⸻ Raise an error if the channel is already COMPLETELY open

    if not channel.locked and not channel.archived:
        await send_bad_request(interaction, subtitle = "This ticket thread is already open.")
        return

    # ⸻ Success!

    await format_send(
        interaction,
        msg_type  = "unlock",
        title     = "Opening thread...",
        ephemeral = False,
    )
    await channel.edit(locked = False, archived = False)
    await set_ticket_state(bot.db, thread_id = channel.id, is_open = True)
