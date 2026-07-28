from typing import final

from discord import Message, Thread
from discord.ext import commands

from bot import Cordex
from constants import (
    DIRECTOR_TASKS_CHANNEL_ID,
    DIRECTORS_ROLE_ID,
    MAIN_GUILD_ID,
    WAPPLE_CHAIN_CHANNEL_ID,
)

from . import WAPPLE_PATTERN

FACTOIDS = {
    "bump" : (
        "# Please bump __both__ bots.\n"
        "We really appreciate everyone bumping! If you are going to bump, please bump **both** <@735147814878969968> and <@1159147139960676422>.\n"
        "### Why?\n"
        "The bots have a cooldown of one bump per 2 hours. We try to sync the timer on each. Bumping both at once ensures that this happens."
    ),
}

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Message Send Handling
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class MessageSendHandler(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def message_send_handler(self, message : Message) -> None:
        content = message.content
        author  = message.author
        channel = message.channel
        guild   = message.guild

        # ⸻ Block the bot itself

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block bots

        if author.bot:
            return

        # ⸻ Block non-guild messages or messages not in the main guild

        if guild is None or guild.id != MAIN_GUILD_ID:
            return

        # ⸻ Block non-wapple text in wapple channel

        if channel.id == WAPPLE_CHAIN_CHANNEL_ID and not WAPPLE_PATTERN.fullmatch(content.strip()):
            await message.delete()
            return

        # ⸻ Factoids

        if content.startswith("?") and " " not in content[1:] and guild.id == MAIN_GUILD_ID:
            key = content[1:].lower()

            if key in FACTOIDS:
                async with channel.typing():
                    await channel.send(FACTOIDS[key])
                    return

        # ⸻ Mention directors upon thread creation

        if isinstance(channel, Thread):
            thread = channel
            if message.id == thread.id and thread.parent_id == DIRECTOR_TASKS_CHANNEL_ID:
                await thread.send(f"<@&{DIRECTORS_ROLE_ID}>")

async def setup(bot : Cordex) -> None:
    cog = MessageSendHandler(bot)
    await bot.add_cog(cog)
