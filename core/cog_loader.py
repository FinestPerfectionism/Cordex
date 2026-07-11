from importlib import import_module
from logging import getLogger as get_logger
from pkgutil import walk_packages

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cog Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

log = get_logger("Cordex")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Cog Discovery
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def discover_cogs(*package_names : str, priority : list[str] | None = None) -> list[str]:
    seen : set[str]  = set()
    cogs : list[str] = []

    for package_name in package_names:
        try:
            package = import_module(package_name)
        except Exception:
            log.exception("Failed to import package %s", package_name)
            continue

        if callable(getattr(package, "setup", None)):
            seen.add(package_name)
            cogs.append(package_name)

        for module_info in walk_packages(
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
                module = import_module(name)
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
