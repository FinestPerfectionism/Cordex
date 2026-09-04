from json import dumps

from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# .eval Tools
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# show_attrs
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def show_attrs(
    target   : object,
    /,
    *,
    tall     : bool | None = None,
    dunders  : bool        = False,
    privates : bool        = False,
) -> str:
    def _filter(attr : str) -> bool:
        if attr.startswith("__") and attr.endswith("__"):
            return dunders
        if attr.startswith("_"):
            return privates
        return True

    attrs = [attr for attr in dir(target) if _filter(attr)]

    if tall is None:
        estimated_length = sum(len(a) for a in attrs) + (2 * (len(attrs) - 1))
        tall = estimated_length > 80

    joiner = ",\n" if tall else ", "

    return codeblock(joiner.join(attrs))

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# format_dict
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_dict(dictionary : dict[str, object], /, *, indent : int = 4) -> str:
    return codeblock(dumps(dictionary, indent = indent))
