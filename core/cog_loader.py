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
    seen : set[str] = set()

    for package_name in package_names:
        try:
            package = import_module(package_name)
        except Exception:
            log.exception("Failed to import package %s", package_name)
            continue

        modules_to_check = [package_name] + [info.name for info in walk_packages(package.__path__, f"{package.__name__}.")]

        for name in modules_to_check:
            if name in seen or name.endswith("._base"):
                continue

            try:
                module = import_module(name)
            except Exception:
                log.exception("Failed to import module %s", name)
                continue

            if callable(getattr(module, "setup", None)):
                seen.add(name)

    if priority:
        priority_set   = set(priority)
        ordered_cogs   = [module_name for module_name in priority if module_name in seen]
        remaining_cogs = sorted([module_name for module_name in seen if module_name not in priority_set])
        return ordered_cogs + remaining_cogs

    return sorted(seen)
