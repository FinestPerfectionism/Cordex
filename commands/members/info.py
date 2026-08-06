from typing import Self, final

from discord import AllowedMentions, MediaGalleryItem, Member
from discord.utils import escape_markdown, format_dt, utcnow

from bot import Interaction
from bot.ui import (
    Container,
    LayoutView,
    MediaGallery,
    TextDisplay,
    Thumbnail,
    ThumbnailSection,
)
from constants import (
    BIG_BOT_EMOJI,
    BOOSTER_EMOJI,
    BOT_OWNER_ID,
    COLOR_GREY,
    DEVELOPER_EMOJI,
    EMPLOYEE_EMOJI,
    OWNER_EMOJI,
    PARTNER_EMOJI,
    PET_CORDEX_EMOJI,
)
from core.utilities import codeblock, format_table, format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /member info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_member_info(
    interaction : Interaction,
    member      : Member | None = None,
    *,
    server      : bool   | None = True,
) -> None:
    await interaction.response.defer()

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    guild  = interaction.guild
    target = member or interaction.user

    if not isinstance(target, Member):
        target = guild.get_member(target.id) or await guild.fetch_member(target.id)

    # ⸻ Sort the joined and roles lists.

    all_members : list[Member] = sorted(
        guild.members,
        key = lambda m : m.joined_at or utcnow(),
    )

    join_list  = "Unknown"
    roles_list = format_values(
        [role.name for role in target.roles if not role.is_default()],
        wrap     = "`",
        use_conj = False,
    )

    # ⸻ Is the user special in anyway?

    characteristics_list = "\n".join(
        filter(
            None,
            [
                f"- {DEVELOPER_EMOJI} This user is **my owner**." if target.id == BOT_OWNER_ID else None,
                f"- {PET_CORDEX_EMOJI} This user is a **good boy**." if interaction.client.user and target.id == interaction.client.user.id else None,
                f"- {EMPLOYEE_EMOJI} This user is a **Discord Employee**." if target.public_flags.staff else None,
                f"- {PARTNER_EMOJI} This user is a **Discord Partner**." if target.public_flags.partner else None,
                f"- {OWNER_EMOJI} This user is the **Server Owner**." if guild.owner_id == target.id else None,
                f"- {BOOSTER_EMOJI} This user is a **Server Booster**." if target.premium_since is not None else None,
            ],
        ),
    )

    if target in all_members:
        target_index = all_members.index(target)

        joined_lines = [
            f"{i + 1:>4}. {"> " if i == target_index else "  "}{str(m) if m.discriminator != "0" else m.name}"
            for i in range(max(0, target_index - 3), min(len(all_members), target_index + 4))
            for m in [all_members[i]]
        ]

        join_list = codeblock("\n".join(joined_lines), language = None) or "Unknown"

    global_user = interaction.client.get_user(target.id) or await interaction.client.fetch_user(target.id)

    # ⸻ Determine avatar and banner based on server parameter.

    avatar = (target.guild_avatar or target.avatar) if server else (target.avatar or global_user.avatar)
    banner = (getattr(target, "guild_banner", None) or global_user.banner) if server else global_user.banner

    # ⸻ Build the view.

    @final
    class InfoView(LayoutView):
        container = Container[Self](
            TextDisplay(f"### {target.mention} {f"| {BIG_BOT_EMOJI} " if target.bot else ""}| {target.id}"),
            color = target.color if (server and target.color.value) else COLOR_GREY,
        )

        user_info = format_table(
            {
                "Name"       : escape_markdown(target.global_name or target.name),
                "Nickname"   : escape_markdown(target.nick or "None") if server else "None",
                "Username"   : escape_markdown(target.name),
                "Joined at"  : f"{format_dt(target.joined_at, style = "F")} | {format_dt(target.joined_at, style = "R")}" if target.joined_at else "Unknown",
                "Created at" : f"{format_dt(target.created_at, style = "F")} | {format_dt(target.created_at, style = "R")}",
            },
        )

        if avatar:
            container.add_item(ThumbnailSection(user_info, thumbnail = Thumbnail(avatar.url)))
        else:
            container.add_text(user_info)

        if roles_list:
            container.add_item(
                TextDisplay(
                    (
                        "**Roles**\n"
                       f"{roles_list}"
                    ),
                ),
            )

        if characteristics_list:
            container.add_item(
                TextDisplay(
                    (
                        "**Characteristics**\n"
                       f"{characteristics_list}"
                    ),
                ),
            )

        if server:
            container.add_item(
                TextDisplay(
                    (
                        "**Join Order**\n"
                        f"{join_list}"
                    ),
                ),
            )

        if banner:
            container.add_item(MediaGallery(MediaGalleryItem(banner.url)))

    await interaction.followup.send(
        view             = InfoView(),
        allowed_mentions = AllowedMentions.none(),
    )
