from asyncio import run
from logging import INFO
from logging import basicConfig as basic_config
from os import getenv
from sys import exit

from dotenv import load_dotenv

from bot import bot, log

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Main Script
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

load_dotenv()

basic_config(
    level  = INFO,
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

TOKEN = getenv("TOKEN")

async def main() -> None:
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
        run(main())
    except KeyboardInterrupt:
        log.info("Received error — KeyboardInterrupt")
    except Exception:
        log.exception("Received fatal error during startup")
        exit(1)
