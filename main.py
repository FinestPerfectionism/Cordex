from asyncio import run
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    WARNING,
    Formatter,
    LogRecord,
    StreamHandler,
)
from logging import getLogger as get_logger
from os import getenv
from sys import exit
from typing import ClassVar, final, override

from dotenv import load_dotenv

from bot import bot, log
from constants import COLOR_BLACK, COLOR_BLUE, COLOR_GREY, COLOR_RED, COLOR_YELLOW


def _hex_to_ansi(hex_value : int) -> str:
    r = (hex_value >> 16) & 0xFF
    g = (hex_value >> 8)  & 0xFF
    b = hex_value         & 0xFF
    return f"\x1b[38;2;{r};{g};{b}m"

@final
class CustomFormatter(Formatter):
    reset   = "\x1b[0m"
    log_fmt = "%(asctime)s | {}%(levelname)s{} | %(name)s | %(message)s"

    FORMATS : ClassVar = {
        DEBUG    : log_fmt.format(_hex_to_ansi(COLOR_GREY.value),   reset),
        INFO     : log_fmt.format(_hex_to_ansi(COLOR_BLUE.value),   reset),
        WARNING  : log_fmt.format(_hex_to_ansi(COLOR_YELLOW.value), reset),
        ERROR    : log_fmt.format(_hex_to_ansi(COLOR_RED.value),    reset),
        CRITICAL : log_fmt.format(_hex_to_ansi(COLOR_BLACK.value),  reset),
    }

    @override
    def format(self, record : LogRecord) -> str:
        log_fmt   = self.FORMATS.get(record.levelno, self.log_fmt)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Main Script
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

load_dotenv()

stream_handler = StreamHandler()
stream_handler.setFormatter(CustomFormatter())

root_logger = get_logger()
root_logger.setLevel(INFO)
root_logger.addHandler(stream_handler)

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
