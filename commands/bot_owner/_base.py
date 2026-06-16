from discord.app_commands import Choice

from bot import Interaction
from core.cog_loader import discover_cogs

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# get_cogs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def get_cogs() -> list[str]:
    return discover_cogs("commands", "events", "core")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# cog_autocomplete
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def cog_autocomplete(_interaction : Interaction, current : str) -> list[Choice[str]]:  # noqa: RUF029
    return [
        Choice(name = cog, value = cog)
        for cog in get_cogs() if current.lower() in cog.lower()
    ][:25]
