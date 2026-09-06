from asyncio import sleep
from secrets import choice
from typing import final

from discord import Message
from discord.ext import commands

from bot import Cordex

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Fun
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class Fun(commands.Cog):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def listener_fun_onmessage(self, message : Message) -> None:
        content   = message.content.lower()
        reference = message.reference
        author    = message.author

        # ⸻ Block bots and the bot itself.

        if author.bot or author == self.bot.user:
            return

        # ⸻ Replies.

        if reference:
            resolved_reference = reference.resolved

            if isinstance(resolved_reference, Message) and resolved_reference.author == self.bot.user:
                greetings = any(trigger in content for trigger in ["hi", "hello"])

                if any([greetings]):
                    responses = ["Hello, human.", "Greetings.", "Hi..?", "Hi... I guess..."]

                    async with message.channel.typing():
                        await sleep(1)
                        await message.reply(content = choice(responses))

async def setup(bot : Cordex) -> None:
    cog = Fun(bot)
    await bot.add_cog(cog)
