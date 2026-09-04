from constants import ACCEPTED_EMOJI, DENIED_EMOJI

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Role Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_permission(name : str, *, value : bool) -> str:
    label = name.replace("_", " ").title()
    emoji = ACCEPTED_EMOJI if value else DENIED_EMOJI
    return f"- {emoji} {label}"
