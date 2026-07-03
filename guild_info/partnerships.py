# ruff: noqa: E501

import time
from typing import Self

import discord
from discord import AllowedMentions, File, HTTPException, NotFound
from discord.ui import (
    Container,
    LayoutView,
    TextDisplay,
    Thumbnail,
)

from bot.ui import (
    HiddenSmallSeparator,
    ThumbnailSection,
    VisibleLargeSeparator,
    VisibleSmallSeparator,
)
from constants import PARTNERSHIP_REQUIREMENTS_CHANNEL_ID, TICKET_CHANNEL_ID
from core.state import (
    IMAGE_DIR,
    PartnershipData,
    PartnershipEntry,
    save_partnership_data,
)

CHARACTERS_PER_GROUP_LIMIT = 4000

type EntryList       = list[PartnershipEntry]
type EntryNestedList = list[list[PartnershipEntry]]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Partnership Views
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class PartnershipComponents1(LayoutView):
    def __init__(self) -> None:
        super().__init__(timeout = None)
        self.add_item(
            Container(
                TextDisplay(
                    content = (
                        "# Welcome to our Partnerships!\n"
                       f"Our server partnerships. Looking to partner? View <#{PARTNERSHIP_REQUIREMENTS_CHANNEL_ID}> then open a __director__ ticket in <#{TICKET_CHANNEL_ID}>.\n"
                        "-# **Note:** It is within Directors' discretion as to whether we choose to partner with your server. "
                        "Directors are not required to provide a reason when denying a partnership."
                    ),
                ),
            ),
        )

class PartnershipComponents2(LayoutView):
    def __init__(self, partnerships : EntryList, timestamp : int) -> None:
        super().__init__(timeout = None)

        children : list[
            TextDisplay[Self]
            | ThumbnailSection
            | VisibleLargeSeparator
            | VisibleSmallSeparator
            | HiddenSmallSeparator
        ] = [
            TextDisplay(
                content = (
                    "# Partnerships\n"
                   f"Partnerships last updated <t:{timestamp}:D>.\n"
                    "-# All partnerships below are subject to removal or update at any time based on Directorate decision. Partnerships are not influenced by the public or other staff.\n"
                    "-# Partnerships assembled by the Directorate team."
                ),
            ),
            HiddenSmallSeparator(),
            VisibleSmallSeparator(),
            HiddenSmallSeparator(),
        ]

        if not partnerships:
            children.append(TextDisplay("Looks like this server has no partnerships! :["))
        else:
            for i, p in enumerate(partnerships):
                children.append(
                    ThumbnailSection(
                        (
                           f"# {p['server_name']}\n"
                            "**Description:**\n"
                           f"> {p['server_description']}\n"
                            "**Server Owner**\n"
                           f"> <@{p['server_owner_id']}>\n"
                           f"[Join Here!]({p['server_link']})"
                        ),
                        thumbnail = Thumbnail(media = f"attachment://{p['image_filename']}"),
                    ),
                )
                if i < len(partnerships) - 1:
                    children.append(VisibleLargeSeparator())

        self.container : Container[LayoutView] = Container(*children)
        self.add_item(self.container)

def estimate_characters(p : PartnershipEntry) -> int:
    return len(
        (
           f"# {p['server_name']}\n"
            "**Description:**\n"
           f"> {p['server_description']}\n"
            "**Server Owner**\n"
           f"> <@{p['server_owner_id']}>\n"
           f"[Join Here!]({p['server_link']})"
        ),
    )

def split_partnerships(partnerships : EntryList) -> EntryNestedList:
    groups        : EntryNestedList = []
    current       : EntryList       = []
    current_chars : int             = 0

    for p in partnerships:
        p_chars = estimate_characters(p)
        if current and current_chars + p_chars > CHARACTERS_PER_GROUP_LIMIT:
            groups.append(current)
            current       = [p]
            current_chars = p_chars
        else:
            current.append(p)
            current_chars += p_chars

    if current:
        groups.append(current)

    return groups

async def rebuild_partnership_layout(channel : discord.TextChannel, data : PartnershipData) -> None:
    for msg_id in data["message_ids"]:
        try:
            msg = await channel.fetch_message(msg_id)
            await msg.delete()
        except (NotFound, HTTPException):
            pass

    header_msg_id = data["header_message_id"]
    if header_msg_id is not None:
        try:
            msg = await channel.fetch_message(header_msg_id)
            await msg.delete()
        except (NotFound, HTTPException):
            pass

    timestamp : int = int(time.time())
    header_msg = await channel.send(view = PartnershipComponents1())

    partnerships = data["partnerships"]
    new_message_ids : list[int] = []

    if not partnerships:
        empty_msg = await channel.send(
            view             = PartnershipComponents2([], timestamp),
            allowed_mentions = AllowedMentions.none(),
        )
        new_message_ids.append(empty_msg.id)
    else:
        for group in split_partnerships(partnerships):
            files : list[File] = [
                File(
                    str(IMAGE_DIR / p["image_filename"]),
                    filename = p["image_filename"],
                )
                for p in group
            ]
            msg = await channel.send(
                view             = PartnershipComponents2(group, timestamp),
                files            = files,
                allowed_mentions = AllowedMentions.none(),
            )
            new_message_ids.append(msg.id)

    data["header_message_id"] = header_msg.id
    data["message_ids"]       = new_message_ids
    data["timestamp"]         = timestamp
    save_partnership_data(data)
