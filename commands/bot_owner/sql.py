from bot import Context
from constants import ACCEPTED_EMOJI, DENIED_EMOJI
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .sql Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


async def run_botowner_sql(ctx : Context, body : str) -> None:
    db = ctx.bot.db

    message = ctx.message
    channel = ctx.channel

    query = "\n".join(body.split("\n")[1 : -1]) if body.startswith("```") else body.strip("` \n")

    try:
        async with db.base_execute(query) as cursor:
            if cursor.description and len(cursor.description) > 0:
                await db.commit()
                await ctx.send(codeblock(str(await cursor.fetchall())))
            else:
                await db.commit()
    except Exception as e:
        await db.rollback()
        await message.add_reaction(DENIED_EMOJI)
        async with channel.typing():
            await ctx.send(codeblock(f"{e.__class__.__name__}: {e}"), delete_after = 15)
        return

    await message.add_reaction(ACCEPTED_EMOJI)
