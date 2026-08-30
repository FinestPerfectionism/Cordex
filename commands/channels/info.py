from typing import TYPE_CHECKING, Self, final

from discord import ForumChannel, StageChannel, TextChannel, Thread, VoiceChannel
from discord.abc import GuildChannel
from discord.utils import format_dt

from bot.ui import Container, LayoutView, TextDisplay
from constants import (
    ACTIVE_LOCKED_STAGE_EMOJI,
    ACTIVE_LOCKED_VOICE_EMOJI,
    ACTIVE_STAGE_EMOJI,
    ACTIVE_VOICE_EMOJI,
    ANNOUNCEMENT_EMOJI,
    ARROW_EMOJI,
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

if TYPE_CHECKING:
    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /channel info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def _is_private(target : GuildChannel) -> bool:
    return not target.permissions_for(target.guild.default_role).view_channel

def _get_channel_emoji(target : GuildChannel) -> str | None:

    # ⸻ target is the rules channel.

    if target.guild.rules_channel and target.id == target.guild.rules_channel.id:
        return RULES_EMOJI

    private = _is_private(target)

    # ⸻ target is a StageChannel.

    if isinstance(target, StageChannel):
        if len(target.members) > 0:
            return ACTIVE_LOCKED_STAGE_EMOJI if private else ACTIVE_STAGE_EMOJI
        return LOCKED_STAGE_EMOJI if private else STAGE_EMOJI

    # ⸻ target is a VoiceChannel.

    if isinstance(target, VoiceChannel):
        if len(target.members) > 0:
            return ACTIVE_LOCKED_VOICE_EMOJI if private else ACTIVE_VOICE_EMOJI
        return LOCKED_VOICE_EMOJI if private else VOICE_EMOJI

    # ⸻ target is a ForumChannel or media channel.

    if isinstance(target, ForumChannel):
        if target.is_media():
            return LOCKED_MEDIA_EMOJI if private else MEDIA_EMOJI
        return LOCKED_FORUM_EMOJI if private else FORUM_EMOJI

    # ⸻ target is a TextChannel or announcement channel.

    if isinstance(target, TextChannel):
        if target.is_news():
            return LOCKED_ANNOUNCEMENT_EMOJI if private else ANNOUNCEMENT_EMOJI
        return LOCKED_TEXT_EMOJI if private else TEXT_EMOJI

    return None

async def run_channel_info(interaction : Interaction, channel : GuildChannel | None = None) -> None:
    await interaction.response.defer()

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

    # ⸻ Channel emoji.

    channel_type_emoji = _get_channel_emoji(target)

    # ⸻ Build the view.

    if thread_target:
        emoji_display = f"| {channel_type_emoji} {ARROW_EMOJI} {THREAD_EMOJI} " if channel_type_emoji else f"| {THREAD_EMOJI} "
        header_text   = f"### {thread_target.mention} {emoji_display}| {thread_target.id}"
    else:
        emoji_display = f"| {channel_type_emoji} " if channel_type_emoji else ""
        header_text   = f"### {target.mention} {emoji_display}| {target.id}"

    topic = getattr(target, "topic", None)

    @final
    class InfoView(LayoutView):
        container = Container[Self](
            TextDisplay(header_text),
            TextDisplay(
                format_table(
                    {
                        "???"               :  "This (mostly) doesn't display any information... yet.",
                        "Not Safe for Work" :  "Yes" if getattr(target, "nsfw", False) else "No",
                        "Created at"        : f"{format_dt(target.created_at, style = "F")} | {format_dt(target.created_at, style = "R")}",
                    },
                ),
            ),
            color = COLOR_GREY,
        )

        if topic:
            container.add_text(
                (
                    "**Description**\n"
                   f"{topic}"
                ),
            )

    await interaction.followup.send(view = InfoView())
