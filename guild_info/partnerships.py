from logging import getLogger as get_logger
from typing import TYPE_CHECKING

from discord import File
from discord.channel import TextChannel
from discord.errors import HTTPException
from discord.threads import Thread
from discord.ui import LayoutView, Thumbnail
from discord.utils import utcnow

from bot.ui import ThumbnailSection
from constants import (
    PARTNERSHIP_REQUIREMENTS_CHANNEL_ID,
    PARTNERSHIPS_CHANNEL_ID,
    TICKETS_CHANNEL_ID,
)
from core.state import IMAGE_DIRECTORY, PartnershipEntry

from ._base import (
    InfoHeaderSection,
    InfoPrimarySection,
    InfoSecondarySection,
    TOSButton,
)

if TYPE_CHECKING:
    from bot import Cordex

CHARACTERS_PER_GROUP_LIMIT = 4000

log = get_logger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Partnership Views
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class PartnershipComponents1(InfoHeaderSection):
    def __init__(self) -> None:
        super().__init__(
            title       =  "our partnerships",
            description = f"Our server partnerships. Looking to partner? View <#{PARTNERSHIP_REQUIREMENTS_CHANNEL_ID}> then open a __director__ ticket in <#{TICKETS_CHANNEL_ID}>",
            note        =  "It is within Directors' discretion as to whether we choose to partner with your server. Directors are not required to provide a reason when denying a partnership.",
        )

class PartnershipComponents2(InfoPrimarySection):
    def __init__(self, text : str | None = None) -> None:
        super().__init__(
            title     = "Partnerships",
            text      = text,
            note      = (
                "-# All partnerships below are subject to removal or update at any time based on Directorate decision. Partnerships are not influenced by the public or other staff.\n"
                "-# Partnerships assembled by the Directorate team."
            ),
            timestamp = utcnow(),
            button    = TOSButton(),
        )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Functions
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def build_partnership_thumbnail_section(entry : PartnershipEntry) -> ThumbnailSection:
    return ThumbnailSection(
        (
           f"# {entry['server_name']}\n"
            "**Description:**\n"
           f"> {entry['server_description']}\n"
            "**Server Owner**\n"
           f"> <@{entry['server_owner_id']}>\n"
           f"[Join Here!]({entry['server_link']})"
        ),
        thumbnail = Thumbnail(media = f"attachment://{entry['image_filename']}"),
    )

def build_partnership_views(entries : list[PartnershipEntry]) -> tuple[list[LayoutView], list[list[File]]]:
    views : list[LayoutView] = [PartnershipComponents1()]
    files : list[list[File]] = [[]]

    # ⸻ If there are no entires, frownies

    if not entries:
        views.append(PartnershipComponents2("Looks like this server has no partnerships! :["))
        files.append([])
        return views, files

    current_view  : InfoPrimarySection | InfoSecondarySection = PartnershipComponents2()
    current_files : list[File]                                = []

    IMAGE_DIRECTORY.mkdir(parents = True, exist_ok = True)

    for entry in entries:
        filename = entry.get("image_filename")
        if not filename:
            log.warning("Skipping entry '%s': missing image filename.", entry.get("server_name", "Unknown"))
            continue

        target_path = IMAGE_DIRECTORY / filename
        if target_path.is_dir() or not target_path.exists():
            log.warning("Skipping entry '%s': image file not found at %s.", entry.get("server_name", "Unknown"), target_path)
            continue

        section = build_partnership_thumbnail_section(entry)
        file    = File(target_path, filename = filename)

        current_view.container.add_item(section)
        current_files.append(file)

        if current_view.content_length() > CHARACTERS_PER_GROUP_LIMIT:
            current_view.container.remove_item(section)
            current_files.pop()

            views.append(current_view)
            files.append(current_files)

            current_view  = InfoSecondarySection()
            current_files = []

            current_view.container.add_item(section)
            current_files.append(file)

    views.append(current_view)
    files.append(current_files)

    return views, files

async def rebuild_partnership_view(
    bot     : "Cordex",
    entries : list[PartnershipEntry],
) -> None:

    # ⸻ First, fetch the channel

    channel = bot.get_channel(PARTNERSHIPS_CHANNEL_ID) or await bot.fetch_channel(PARTNERSHIPS_CHANNEL_ID)

    # ⸻ Make sure it's a valid channel to send views to

    if not isinstance(channel, TextChannel | Thread):
        error = f"{PARTNERSHIPS_CHANNEL_ID} is not a text channel or thread."
        raise TypeError(error)

    # ⸻ Clear every single message in the channel before we rebuild

    async for message in channel.history(limit = None):
        try:
            await message.delete()
        except HTTPException:
            log.exception(
                "Failed to delete message %s in #%s.",
                message.id,
                channel.id,
            )

    payloads : list[tuple[InfoPrimarySection | InfoSecondarySection, list[File]]] = []

    # ⸻ If there are no entires, frownies

    if not entries:
        payloads.append(
            (
                PartnershipComponents2("Looks like this server has no partnerships! :["),
                [],
            ),
        )
    else:
        current_view  : InfoPrimarySection | InfoSecondarySection = PartnershipComponents2()
        current_files : list[File]                                = []

        IMAGE_DIRECTORY.mkdir(parents = True, exist_ok = True)

        for entry in entries:
            filename = entry.get("image_filename")
            if not filename:
                log.warning("Skipping entry '%s': missing image filename.", entry.get("server_name", "Unknown"))
                continue

            target_path = IMAGE_DIRECTORY / filename
            if target_path.is_dir() or not target_path.exists():
                log.warning("Skipping entry '%s': image file not found at %s.", entry.get("server_name", "Unknown"), target_path)
                continue

            section = build_partnership_thumbnail_section(entry)
            file    = File(target_path, filename = filename)

            current_view.container.add_item(section)
            current_files.append(file)

            if current_view.content_length() > CHARACTERS_PER_GROUP_LIMIT:
                current_view.container.remove_item(section)
                current_files.pop()

                payloads.append((current_view, current_files))

                current_view  = InfoSecondarySection()
                current_files = []

                current_view.container.add_item(section)
                current_files.append(file)

        payloads.append((current_view, current_files))

    new_message_ids : list[int] = []

    header_message = await channel.send(view = PartnershipComponents1())
    new_message_ids.append(header_message.id)

    for view, files in payloads:
        message = await channel.send(view = view, files = files)
        new_message_ids.append(message.id)

    # ⸻ Clear old messages from the database since we deleted them earlier

    await bot.db.execute(
        "DELETE FROM guild_info WHERE channel_id = ?",
        [str(PARTNERSHIPS_CHANNEL_ID)],
    )

    await bot.db.executemany(
        """
        INSERT INTO guild_info (
            channel_id,
            position,
            message_id
        )
        VALUES (?, ?, ?)
        """,
        [
            (PARTNERSHIPS_CHANNEL_ID, position, message_id)
            for position, message_id in enumerate(new_message_ids)
        ],
    )

    await bot.db.commit()
