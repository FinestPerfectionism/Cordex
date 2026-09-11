from typing import Self, final

from discord import AllowedMentions, MediaGalleryItem, Member

from bot import Interaction
from bot.ui import Container, LayoutView, MediaGallery, TextDisplay
from constants import COLOR_GREY
from core.exceptions import send_bad_argument

from ._base import Scope

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /member banner Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_member_banner(
    interaction : Interaction,
    member      : Member | None = None,
    scope       : Scope  | None = "global",
) -> None:
    await interaction.response.defer()

    client_user = interaction.client.user

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    target = member or interaction.user

    guild = interaction.guild

    if guild is None or not isinstance(target, Member):
        return

    # ⸻ Determine banner based on server parameter.

    fetched_target = await interaction.client.fetch_user(target.id)
    guild_target   = guild.get_member(target.id) or await guild.fetch_member(target.id)

    banner = (guild_target.guild_banner if scope == "guild" else None) or fetched_target.banner

    if not banner:
        if target == interaction.user:
            await send_bad_argument(
                interaction,
                subtitle = {"member" : "You do not have a banner set."},
            )
            return

        if target == client_user:
            await send_bad_argument(
                interaction,
                subtitle = {"member" : "I do not have a banner set."},
            )
            return

        await send_bad_argument(
            interaction,
            subtitle = {"member" : f"{target.mention} does not have a banner set."},
        )
        return

    if target == client_user:
        mention = "My"
        name    = "my"
    elif target == interaction.user:
        mention = "Your"
        name    = "your"
    else:
        mention = f"{target.mention}'s'"
        name    = f"{target.name}'s'"

    @final
    class BannerView(LayoutView):
        container = Container[Self](
            TextDisplay(f"### {mention} Banner"),
            TextDisplay(f"View {name} banner [here]({banner.url})."),
            MediaGallery(MediaGalleryItem(banner.url)),
            color = target.color if target.color.value else COLOR_GREY,
        )

    await interaction.followup.send(
        view             = BannerView(),
        allowed_mentions = AllowedMentions.none(),
    )
