import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from bot import bot, log

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Main Script
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

_ = load_dotenv()

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

TOKEN = os.getenv("TOKEN")

async def main() -> None:
    if not TOKEN:
        warning = "TOKEN environment variable not set."
        raise RuntimeError(warning)

    log.info("Starting Discord connection")

    try:
        await bot.start(TOKEN.strip())
    except Exception:
        log.exception("Received error — Bot crashed during runtime")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Received error — KeyboardInterrupt")
    except Exception:
        log.exception("Received fatal error during startup")
        sys.exit(1)
