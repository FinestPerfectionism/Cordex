from discord import ForumChannel, StageChannel, TextChannel, VoiceChannel
from discord.abc import GuildChannel

from bot import Interaction
from core.exceptions import send_bad_argument
from core.responses import format_send

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /channel sync Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_channel_sync(
    interaction : Interaction,
    channel     : GuildChannel | None = None,
) -> None:
    await interaction.response.defer(ephemeral = True)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    target = channel or interaction.channel

    if isinstance(target, TextChannel | VoiceChannel | StageChannel | ForumChannel):
        if target.category:
            await target.edit(sync_permissions = True)
            await format_send(
                interaction,
                msg_type = "success",
                title    = "synced channel",
            )
            return
        await send_bad_argument(interaction, subtitle = {"channel" : "Channel must be under a category"})
        return
