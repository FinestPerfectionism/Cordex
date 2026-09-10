import sys
from asyncio import run
from logging import INFO
from logging import basicConfig as basic_config
from os import getenv

from dotenv import load_dotenv

from bot import Cordex, log

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Main Script
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

load_dotenv()

basic_config(
    level  = INFO,
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

TOKEN = getenv("TOKEN")

bot = Cordex()
async def _main() -> None:
    if not TOKEN:
        error = "TOKEN environment variable not set."
        raise RuntimeError(error)

    log.info("Starting Discord connection")

    async with bot:
        try:
            await bot.start(TOKEN.strip())
        except Exception:
            log.exception("Received error — Bot crashed during runtime")


if __name__ == "__main__":
    try:
        run(_main())
    except KeyboardInterrupt:
        log.info("Received error — KeyboardInterrupt")
    except Exception:
        log.exception("Received fatal error during startup")
        sys.exit(1)
