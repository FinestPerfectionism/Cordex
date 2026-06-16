import importlib
import os
import pathlib
import pkgutil
from logging import Logger, getLogger
from typing import override

from discord.ext import commands, tasks

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cog Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

log : Logger = getLogger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cog Discovery
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def discover_cogs(*package_names : str, priority : list[str] | None = None) -> list[str]:
    seen : set[str]  = set()
    cogs : list[str] = []

    for package_name in package_names:
        try:
            package = importlib.import_module(package_name)
        except Exception:
            log.exception("Failed to import package %s", package_name)
            continue

        if callable(getattr(package, "setup", None)):
            seen.add(package_name)
            cogs.append(package_name)

        for module_info in pkgutil.walk_packages(
            package.__path__,
            prefix = f"{package.__name__}.",
        ):
            name = module_info.name
            short_name = name.split(".")[-1]

            if name in seen:
                continue

            if short_name == "_base":
                continue

            try:
                module = importlib.import_module(name)
            except Exception:
                log.exception("Failed to import module %s", name)
                continue

            if callable(getattr(module, "setup", None)):
                seen.add(name)
                cogs.append(name)

    if priority:
        priority_set   = set(priority)
        ordered_cogs   = [m for m in priority if m in seen]
        remaining_cogs = [m for m in cogs if m not in priority_set]
        cogs           = ordered_cogs + sorted(remaining_cogs)
    else:
        cogs = sorted(cogs)

    return cogs

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cog Auto-Reloading
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


IGNORE_EXTENSIONS = []

def path_from_extension(extension : str) -> pathlib.Path:
    return pathlib.Path(extension.replace(".", os.sep) + ".py")

class CogAutoReloading(commands.Cog):
    def __init__(self, bot : commands.Bot, *package_names : str) -> None:
        self.bot                : commands.Bot     = bot
        self.package_names      : tuple[str, ...]  = package_names
        self.last_modified_time : dict[str, float] = {}
        _ = self.hot_reload_loop.start()

    @override
    async def cog_unload(self) -> None:
        self.hot_reload_loop.stop()

    @tasks.loop(seconds = 3)
    async def hot_reload_loop(self) -> None:
        current_extensions    = list(self.bot.extensions.keys())
        discovered_extensions = discover_cogs(*self.package_names)

        all_extensions = list(set(current_extensions + discovered_extensions))

        for extension in all_extensions:
            if extension in IGNORE_EXTENSIONS:
                continue

            path = path_from_extension(extension)
            try:
                time = path.stat().st_mtime
            except OSError:
                continue

            last_time = self.last_modified_time.get(extension)
            if last_time == time:
                continue

            self.last_modified_time[extension] = time
            if last_time is None and extension in self.bot.extensions:
                continue

            try:
                if extension in self.bot.extensions:
                    await self.bot.reload_extension(extension)
                else:
                    await self.bot.load_extension(extension)
            except commands.ExtensionError:
                log.exception("Failed to load cog %s", extension)
            else:
                log.info("Reloaded cog %s", extension)

        for ext in list(self.last_modified_time.keys()):
            if ext not in self.bot.extensions:
                del self.last_modified_time[ext]

    @hot_reload_loop.before_loop
    async def cache_last_modified_time(self) -> None:
        discovered_extensions = discover_cogs(*self.package_names)
        for extension in discovered_extensions:
            if extension in IGNORE_EXTENSIONS:
                continue
            path = path_from_extension(extension)
            try:
                time = path.stat().st_mtime
                self.last_modified_time[extension] = time
            except OSError:
                pass

async def setup(bot : commands.Bot) -> None:
    cog = CogAutoReloading(bot, "events", "core", "commands")
    await bot.add_cog(cog)
