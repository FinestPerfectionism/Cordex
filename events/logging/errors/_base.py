# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Errors Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# get_bad_argument_subtitle
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def get_bad_argument_subtitle(subtitle : dict[str, str]) -> str:
    return "\n".join(f"`{arg}`: {notice}" for arg, notice in subtitle.items())

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# get_bad_operation_subtitle
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def get_bad_operation_title(title : str) -> str:
    return title

def get_bad_operation_subtitle(subtitle : str | None) -> str:
    return subtitle if subtitle else "An exception occurred while running this command."

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# get_bad_permissions_subtitle
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def get_bad_permissions_subtitle(arguments : tuple[str, ...]) -> str:
    formatted_args = [f"`{arg}`" for arg in arguments]
    if len(formatted_args) == 1:
        return f"You are not authorized to use the {formatted_args[0]} argument."
    return f"You are not authorized to use these arguments: {', '.join(formatted_args)}"
