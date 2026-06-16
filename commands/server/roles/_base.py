from constants import ACCEPTED_EMOJI, DENIED_EMOJI

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Role Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def format_permission(perm_name : str, *, value : bool) -> str:
    label = perm_name.replace("_", " ").title()
    mark  = ACCEPTED_EMOJI if value else DENIED_EMOJI
    return f"- {mark} {label}"
