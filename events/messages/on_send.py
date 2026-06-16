import contextlib
import re

import discord
from discord.ext import commands

from bot import Cordex, log
from constants import (
    ACCEPTED_EMOJI,
    DIRECTOR_TASKS_CHANNEL_ID,
    DIRECTORS_ROLE_ID,
    STAFF_COMMITTEE_ROLE_ID,
    STAFF_PROPOSALS_CHANNEL_ID,
    STAFF_PROPOSALS_REVIEW_CHANNEL_ID,
    WAPPLE_CHAIN_CHANNEL_ID,
)

from ._base import WAPPLE_PATTERN

FACTOIDS = {
    "bump"   : (
        "# Please bump __both__ bots.\n"
        "We really appreciate everyone bumping! If you are going to bump, please bump **both** <@735147814878969968> and <@1159147139960676422>.\n"
        "### Why?\n"
        "The bots have a cooldown of one bump per 2 hours. We try to sync the timer on each. Bumping both at once ensures that this happens."
    ),
}

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Send Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class MessageSendHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot : Cordex = bot

    @commands.Cog.listener("on_message")
    async def message_send_handler(self, message : discord.Message) -> None:
        if message.author.bot:
            return

        content = message.content

        if content.startswith("?") and " " not in content[1:] and message.guild:
            key = content[1:].lower()

            if key in FACTOIDS:
                async with message.channel.typing():
                    _ = await message.channel.send(FACTOIDS[key])
                    return

        if message.channel.id == WAPPLE_CHAIN_CHANNEL_ID:
            content = message.content.strip()

            if not WAPPLE_PATTERN.fullmatch(content):
                with contextlib.suppress(discord.HTTPException):
                    await message.delete()
            return

        if isinstance(message.channel, discord.Thread):
            thread = message.channel
            if thread.name.lower() not in {"test", "t"} and message.id == thread.id:
                if thread.parent_id == STAFF_PROPOSALS_CHANNEL_ID:
                    committee_forum = self.bot.get_channel(STAFF_PROPOSALS_REVIEW_CHANNEL_ID)
                    if isinstance(committee_forum, discord.ForumChannel):
                        _ = await committee_forum.create_thread(
                            name    = f"SCR: {thread.name}",
                            content = (
                                f"{ACCEPTED_EMOJI} **A new proposal has been posted: {thread.mention}**\n"
                                f"<@&{STAFF_COMMITTEE_ROLE_ID}>\n"
                            ),
                        )

                if thread.parent_id == DIRECTOR_TASKS_CHANNEL_ID:
                    try:
                        _ = await thread.send(content = f"<@&{DIRECTORS_ROLE_ID}>")
                    except Exception:
                        log.exception("Failed to send director role mention")

        if (
            "https://tenor.com/view/dog-funny-video-funny-funny-dog-dog-peeing-gif-4718562751207105873"
            in (message.content or "").lower()
        ):
            warning = await message.channel.send(f"{message.author.mention} Hey dude, can you like *not* send that GIF? You're really not that funny.")
            await warning.delete(delay = 15)
            return

        if re.search(r"\b67\b", message.content) and message.guild and message.guild.id:
            await message.add_reaction("<:67:1484198860263002133>")

async def setup(bot : Cordex) -> None:
    cog = MessageSendHandler(bot)
    await bot.add_cog(cog)
