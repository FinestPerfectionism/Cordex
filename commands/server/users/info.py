from discord import MediaGalleryItem, Member, utils
from discord.ui import Container, LayoutView, MediaGallery, TextDisplay, Thumbnail
from discord.utils import format_dt

from bot import Interaction
from bot.ui import ThumbnailSection
from constants import BOT_STRING, COLOR_GREY
from core.utilities import codeblock, format_values

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /user info Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_user_info(interaction : Interaction, user : Member | None = None):
    await interaction.response.defer()

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
        key = lambda m : m.joined_at or utils.utcnow(),
    )

    join_list  : str = ""
    roles_list : str = format_values(
        [role.name for role in target.roles if not role.is_default()],
        wrap     = "`",
        use_conj = False,
    )

    if target in all_members:
        target_index : int = all_members.index(target)

        start_index : int = max(0, target_index - 3)
        end_index   : int = min(len(all_members), target_index + 4)

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
        container : Container[LayoutView] = Container(accent_color = target.color if target.color.value else COLOR_GREY)
        container.add_item(TextDisplay(f"### {target.mention} | {target.id}{f" | {BOT_STRING}" if target.bot else ""}"))

        user_info : str = (
            f"`       Name:` {target.global_name}\n"
            f"`   Nickname:` {target.nick or 'None'}\n"
            f"`   Username:` {target.name}\n"
            f"`  Joined at:` {format_dt(target.joined_at, style = 'F') if target.joined_at else 'Unknown'}\n"
            f"` Created at:` {format_dt(target.created_at, style = 'F')}\n"
        )

        if target.avatar:
            container.add_item(
                ThumbnailSection(
                    user_info,
                    thumbnail = Thumbnail(target.avatar.url),
                ),
            )
        else:
            container.add_item(TextDisplay(user_info))

        container.add_item(
            TextDisplay(

                    "**Roles**\n"
                   f"{roles_list or "None"}",

            ),
        )
        container.add_item(
            TextDisplay(

                    "**Join Order**\n"
                   f"{join_list}",

            ),
        )

        if member.banner:
            container.add_item(MediaGallery(MediaGalleryItem(member.banner.url)))

    await interaction.followup.send(view = InfoView(), ephemeral = True)
