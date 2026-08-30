from typing import TYPE_CHECKING, Self, final

from discord import AllowedMentions, MediaGalleryItem, VerificationLevel
from discord.utils import format_dt

from bot.ui import (
    Container,
    LayoutView,
    MediaGallery,
    TextDisplay,
    Thumbnail,
    ThumbnailSection,
)
from constants import (
    BOOSTED_GLOBAL_SERVER_EMOJI,
    BOOSTED_SERVER_EMOJI,
    CATEGORY_EMOJI,
    COLOR_GREY,
    FORUM_EMOJI,
    GLOBAL_SERVER_EMOJI,
    PARTNERED_SERVER_EMOJI,
    SERVER_EMOJI,
    STAGE_EMOJI,
    TEXT_EMOJI,
    VERIFIED_SERVER_EMOJI,
    VOICE_EMOJI,
)
from core.exceptions import send_bad_operation
from core.utilities import format_table

if TYPE_CHECKING:
    from bot import Interaction

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

verification_level_map = {
    VerificationLevel.none    : "Off",
    VerificationLevel.low     : "Low",
    VerificationLevel.medium  : "Medium",
    VerificationLevel.high    : "High",
    VerificationLevel.highest : "Max",
}
verification_requirement_map = {
    VerificationLevel.none    : "Unrestricted",
    VerificationLevel.low     : "Must be verified via email",
    VerificationLevel.medium  : "Must be registered for more than 5 minutes",
    VerificationLevel.high    : "Must be a member for more than 10 minutes",
    VerificationLevel.highest : "Must be verified via phone number",
}

async def run_server_info(interaction : Interaction) -> None:
    await interaction.response.defer()

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    guild = interaction.guild
    if not (owner := guild.owner):
        if guild.owner_id is not None:
            owner = await guild.fetch_member(guild.owner_id)
        else:
            await send_bad_operation(interaction, subtitle = "Fetching the guild owner failed repeatedly.")
            return

    member_total = guild.member_count or 0
    bots         = sum(1 for member in guild.members if member.bot)
    humans       = member_total - bots

    channel_text = (
        f"{len(guild.text_channels)} {TEXT_EMOJI}, "
        f"{len(guild.voice_channels)} {VOICE_EMOJI}, "
        f"{len(guild.categories)} {CATEGORY_EMOJI}, "
        f"{len(guild.stage_channels)} {STAGE_EMOJI}, "
        f"{len(guild.forums)} {FORUM_EMOJI} | "
        f"{len(guild.channels)} total"
    )

    boost_level = guild.premium_tier
    boost_count = guild.premium_subscription_count

    verification_level       = verification_level_map.get(guild.verification_level, "Unknown")
    verification_requirement = verification_requirement_map.get(guild.verification_level, "Unknown")

    match guild.features:
        case _ if "PARTNERED" in guild.features:
            server_type_emoji = PARTNERED_SERVER_EMOJI
        case _ if "VERIFIED" in guild.features:
            server_type_emoji = VERIFIED_SERVER_EMOJI
        case _ if "DISCOVERABLE" in guild.features and boost_count > 0:
            server_type_emoji = BOOSTED_GLOBAL_SERVER_EMOJI
        case _ if "COMMUNITY" in guild.features and boost_count > 0:
            server_type_emoji = BOOSTED_SERVER_EMOJI
        case _ if "DISCOVERABLE" in guild.features:
            server_type_emoji = GLOBAL_SERVER_EMOJI
        case _ if "COMMUNITY" in guild.features:
            server_type_emoji = SERVER_EMOJI
        case _:
            server_type_emoji = None

    @final
    class InfoView(LayoutView):
        container = Container[Self](
            TextDisplay(f"### {guild.name} {f"| {server_type_emoji} " if server_type_emoji else ""}| {guild.id}"),
            color = owner.color if owner.color.value else COLOR_GREY,
        )

        guild_info = format_table(
            {
                "Owner"         : f"{owner.mention} | {owner.id}",
                "Icon"          : f"[Icon Link]({guild.icon.url})" if guild.icon else "None",
                "Verification"  : f"{verification_level} | {verification_requirement}",
                "2FA"           :  "Enabled" if guild.mfa_level else "Disabled",
                "Roles"         : f"{len(guild.roles)}",
                "Members"       : f"{humans} humans, {bots} bots | {member_total} total",
                "Channels"      : channel_text,
                "Server Boosts" : f"Level {boost_level} | {boost_count} boosts total",
                "Vanity Link"   : guild.vanity_url or "None",
                "Created at"    : f"{format_dt(guild.created_at, style = "F")} | {format_dt(guild.created_at, style = "R")}",
            },
        )

        if guild.icon:
            container.add_item(ThumbnailSection(guild_info, thumbnail = Thumbnail(guild.icon.url)))
        else:
            container.add_text(guild_info)
        if guild.banner:
            container.add_item(MediaGallery(MediaGalleryItem(guild.banner.url)))

    await interaction.followup.send(
        view             = InfoView(),
        allowed_mentions = AllowedMentions.none(),
    )
