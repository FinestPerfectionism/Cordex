from typing import Self

from discord import ForumChannel, StageChannel, TextChannel, Thread, VoiceChannel
from discord.abc import GuildChannel
from discord.ui import Container, LayoutView, TextDisplay

from bot import Interaction
from constants import (
    ACTIVE_LOCKED_STAGE_EMOJI,
    ACTIVE_LOCKED_VOICE_EMOJI,
    ACTIVE_STAGE_EMOJI,
    ACTIVE_VOICE_EMOJI,
    ANNOUNCEMENT_EMOJI,
    COLOR_GREY,
    FORUM_EMOJI,
    LOCKED_ANNOUNCEMENT_EMOJI,
    LOCKED_FORUM_EMOJI,
    LOCKED_MEDIA_EMOJI,
    LOCKED_STAGE_EMOJI,
    LOCKED_TEXT_EMOJI,
    LOCKED_VOICE_EMOJI,
    MEDIA_EMOJI,
    RULES_EMOJI,
    STAGE_EMOJI,
    TEXT_EMOJI,
    THREAD_EMOJI,
    VOICE_EMOJI,
)
from core.utilities import format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server channel info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def is_private(channel : GuildChannel) -> bool:
    return not channel.permissions_for(channel.guild.default_role).view_channel

async def run_server_channel_info(
    interaction : Interaction,
    channel     : GuildChannel | None = None,
    *,
    ephemeral   : bool                = True,
) -> None:
    await interaction.response.defer(ephemeral = ephemeral)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    target = channel or interaction.channel
    thread_target : Thread | None = None

    if isinstance(target, Thread):
        thread_target = target
        target = target.parent

    if not isinstance(target, GuildChannel):
        return

    # ⸻ Channel emoji

    channel_type_emoji = None

    if target.guild.rules_channel and target.id == target.guild.rules_channel.id:
        channel_type_emoji = RULES_EMOJI

    elif isinstance(target, StageChannel) and is_private(target) and len(target.members) > 0:
        channel_type_emoji = ACTIVE_LOCKED_STAGE_EMOJI
    elif isinstance(target, StageChannel) and len(target.members) > 0:
        channel_type_emoji = ACTIVE_STAGE_EMOJI
    elif isinstance(target, StageChannel) and is_private(target):
        channel_type_emoji = LOCKED_STAGE_EMOJI
    elif isinstance(target, StageChannel):
        channel_type_emoji = STAGE_EMOJI

    elif isinstance(target, VoiceChannel) and is_private(target) and len(target.members) > 0:
        channel_type_emoji = ACTIVE_LOCKED_VOICE_EMOJI
    elif isinstance(target, VoiceChannel) and len(target.members) > 0:
        channel_type_emoji = ACTIVE_VOICE_EMOJI
    elif isinstance(target, VoiceChannel) and is_private(target):
        channel_type_emoji = LOCKED_VOICE_EMOJI
    elif isinstance(target, VoiceChannel):
        channel_type_emoji = VOICE_EMOJI

    elif isinstance(target, ForumChannel) and target.is_media() and is_private(target):
        channel_type_emoji = LOCKED_MEDIA_EMOJI
    elif isinstance(target, ForumChannel) and target.is_media():
        channel_type_emoji = MEDIA_EMOJI

    elif isinstance(target, ForumChannel) and is_private(target):
        channel_type_emoji = LOCKED_FORUM_EMOJI
    elif isinstance(target, ForumChannel):
        channel_type_emoji = FORUM_EMOJI

    elif isinstance(target, TextChannel) and target.is_news() and is_private(target):
        channel_type_emoji = LOCKED_ANNOUNCEMENT_EMOJI
    elif isinstance(target, TextChannel) and target.is_news():
        channel_type_emoji = ANNOUNCEMENT_EMOJI

    elif isinstance(target, TextChannel) and is_private(target):
        channel_type_emoji = LOCKED_TEXT_EMOJI
    elif isinstance(target, TextChannel):
        channel_type_emoji = TEXT_EMOJI

    # ⸻ Build the view

    if thread_target:
        emoji_display   = f"| {channel_type_emoji} ➔ {THREAD_EMOJI} " if channel_type_emoji else f"| {THREAD_EMOJI} "
        mention_display = f"{target.mention} ➔ {thread_target.mention}"
        id_display      = thread_target.id
    else:
        emoji_display   = f"| {channel_type_emoji} " if channel_type_emoji else ""
        mention_display = target.mention
        id_display      = target.id

    class InfoView(LayoutView):
        container : Container[Self] = Container[Self](
            TextDisplay(f"### {mention_display} {emoji_display}| {id_display}"),
            TextDisplay(
                format_table(
                    {
                        "???" : "This doesn't display any information... yet.",
                    },
                    padding = 0,
                ),
            ),
            accent_color = COLOR_GREY,
        )

    await interaction.followup.send(view = InfoView(), ephemeral = ephemeral)
