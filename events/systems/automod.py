from collections import defaultdict
from time import time

from discord import Message, Member
from discord.ext import commands

from bot import Cordex
from constants import STAFF_ROLES

BANNED_GIF = "https://tenor.com/view/dog-funny-video-funny-funny-dog-dog-peeing-gif-4718562751207105873"

TRIGGER_SECONDS = 10.0
TRIGGER_PHOTOS  = 5

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Auto-Moderation System
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class AutomoderationSystem(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot  : Cordex                 = bot
        self.heat : dict[int, list[float]] = defaultdict(list)

    @commands.Cog.listener("on_message")
    async def automoderation_system(self, message : Message) -> None:
        content = message.content
        author  = message.author

        # ⸻ Block the bot itself

        if author.bot or author == self.bot.user:
            return

        # ⸻ Block non-guild messages

        if message.guild is None:
            return

        # ⸻ Immediate Infraction Checks

        if BANNED_GIF in content:
            await message.delete()
            return

        # ⸻ Auto-Moderation Logic

        has_image = bool(
            message.attachments
            or message.embeds
            or any(ext in content.lower() for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"])
            or "tenor.com/view" in content.lower(),
        )

        if has_image and isinstance(author, Member):
            # 1 ~~~ Switch from a raw STAFF_ROLES to check to a legitimate function.
            if any(role.id in STAFF_ROLES for role in author.roles):
                return
            else:
                current_time = time()
                user_heat = self.heat[author.id]
    
                user_heat[:] = [t for t in user_heat if current_time - t < TRIGGER_SECONDS]
                user_heat.append(current_time)
    
                if len(user_heat) >= TRIGGER_PHOTOS:
                    await author.ban(reason = "Auto-Moderation: Image Spam")
                    del self.heat[author.id]

async def setup(bot : Cordex) -> None:
    cog = AutomoderationSystem(bot)
    await bot.add_cog(cog)
