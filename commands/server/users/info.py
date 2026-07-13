from typing import Self

from discord import MediaGalleryItem, Member
from discord.ui import Container, LayoutView, MediaGallery, TextDisplay, Thumbnail
from discord.utils import escape_markdown, format_dt, utcnow

from bot import Interaction
from bot.ui import ThumbnailSection
from constants import (
    BIG_BOT_EMOJI,
    BOOSTER_EMOJI,
    COLOR_GREY,
    EMPLOYEE_EMOJI,
    OWNER_EMOJI,
    PARTNER_EMOJI,
)
from core.utilities import codeblock, format_table, format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /user info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_user_info(
    interaction : Interaction,
    user        : Member | None = None,
    *,
    ephemeral   : bool          = True,
) -> None:
    await interaction.response.defer(ephemeral = ephemeral)

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    guild  = interaction.guild
    target = user or interaction.user

    if not isinstance(target, Member):
        target = guild.get_member(target.id) or await guild.fetch_member(target.id)

    member = await interaction.client.fetch_user(target.id)

    # ⸻ Sort the joined and roles lists

    all_members : list[Member] = sorted(
        guild.members,
        key = lambda m : m.joined_at or utcnow(),
    )

    join_list       : str = ""
    roles_list      : str = format_values(
        [role.name for role in target.roles if not role.is_default()],
        wrap     = "`",
        use_conj = False,
    )
    characteristics : list[str] = []

    # ⸻ Is the user special in anyway?

    if interaction.client.user and target.id == interaction.client.user.id:
        characteristics.append("- <a:pet_cordex:1526024713078571141> This user is a **good boy**.")
    if target.public_flags.staff:
        characteristics.append(f"- {EMPLOYEE_EMOJI} This user is a **Discord Employee**.")
    if target.public_flags.partner:
        characteristics.append(f"- {PARTNER_EMOJI} This user is a **Discord Partner**.")
    if guild.owner_id == target.id:
        characteristics.append(f"- {OWNER_EMOJI} This user is the **Server Owner**.")
    if target.premium_since is not None:
        characteristics.append(f"- {BOOSTER_EMOJI} This user is a **Server Booster**.")

    characteristics_list : str = "\n".join(characteristics)

    if target in all_members:
        target_index : int = all_members.index(target)
        start_index  : int = max(0, target_index - 3)
        end_index    : int = min(len(all_members), target_index + 4)

        joined_lines : list[str] = []

        for i in range(start_index, end_index):
            current_member : Member = all_members[i]
            position       : int = i + 1

            username  : str = str(current_member) if current_member.discriminator != "0" else current_member.name
            indicator : str = "> " if i == target_index else "  "

            joined_lines.append(f"{position:>4}. {indicator}{username}")

        join_list = codeblock("\n".join(joined_lines), language = None) or "Unknown"

    # ⸻ Build the view

    class InfoView(LayoutView):
        def __init__(self) -> None:
            super().__init__(timeout = None)
            container : Container[Self] = Container(
                TextDisplay(f"### {target.mention} {f"| {BIG_BOT_EMOJI} " if target.bot else ""}| {target.id}"),
                accent_color = target.color if target.color.value else COLOR_GREY,
            )

            user_info : str = format_table(
                {
                    "Name"       : escape_markdown(target.global_name or target.name),
                    "Nickname"   : escape_markdown(target.nick or "None"),
                    "Username"   : escape_markdown(target.name),
                    "Joined at"  : format_dt(target.joined_at, style = "F") if target.joined_at else "Unknown",
                    "Created at" : format_dt(target.created_at, style = "F"),
                },
            )

            if target.avatar:
                container.add_item(ThumbnailSection(user_info, thumbnail = Thumbnail(target.avatar.url)))
            else:
                container.add_item(TextDisplay(user_info))

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

            container.add_item(
                TextDisplay(
                    (
                        "**Join Order**\n"
                       f"{join_list}"
                    ),
                ),
            )

            if member.banner:
                container.add_item(MediaGallery(MediaGalleryItem(member.banner.url)))

            self.add_item(container)

    await interaction.followup.send(view = InfoView(), ephemeral = ephemeral)
