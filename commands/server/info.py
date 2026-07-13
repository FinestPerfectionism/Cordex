from typing import Self
from discord import VerificationLevel
from discord.ui import LayoutView, Thumbnail, Container, TextDisplay
from discord.utils import format_dt
from bot import Interaction
from bot.ui import ThumbnailSection
from constants import (
    BOOSTED_GLOBAL_SERVER_EMOJI,
    BOOSTED_SERVER_EMOJI,
    COLOR_GREY,
    GLOBAL_SERVER_EMOJI,
    PARTNERED_SERVER_EMOJI, 
    SERVER_EMOJI,
    VERIFIED_SERVER_EMOJI,
)
from core.exceptions import send_bad_operation
from core.utilities import format_table

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_server_info(interaction : Interaction) -> None:
    await interaction.response.defer(ephemeral = True)

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

    text          = len(guild.text_channels)
    voice         = len(guild.voice_channels)
    categories    = len(guild.categories)
    stage         = len(guild.stage_channels)
    forum         = len(guild.forums)
    channel_total = len(guild.channels)

    boost_level = guild.premium_tier
    boost_count = guild.premium_subscription_count

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

    class InfoView(LayoutView):
        container : Container[Self] = Container(
            TextDisplay(f"### {guild.name} {f"| {server_type_emoji} " if server_type_emoji else ""}| {guild.id}"),
            accent_colour = owner.color if owner.color.value else COLOR_GREY,
        )

        guild_info : str = format_table(
            {
                "Owner"         : f"{owner.mention} | {owner.id}",
                "Icon"          : f"[Icon Link]({guild.icon.url})" if guild.icon else "None",
                "Verification"  : f"{verification_level} | {verification_requirement}",
                "2FA"           :  "Enabled" if guild.mfa_level else "Disabled",
                "Roles"         : f"{len(guild.roles)}",
                "Members"       : f"{humans} humans, {bots} bots | {member_total} total",
                "Channels"      : f"{text} text, {voice} voice, {categories} categories, {stage} stage, {forum} forum | {channel_total} total",
                "Server Boosts" : f"Level {boost_level} | {boost_count} boosts total",
                "Created at"    : format_dt(guild.created_at, style = "F")
            }
        )

        if guild.icon:
            container.add_item(ThumbnailSection(guild_info, thumbnail = Thumbnail(guild.icon.url)))
        else:
            container.add_item(TextDisplay(guild_info))

    await interaction.followup.send(view = InfoView(), ephemeral = True)
