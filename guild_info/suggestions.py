from constants import BOT_OWNER_MENTION

from ._base import InfoHeaderSection, InfoPrimarySection

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Suggestions Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class SuggestionComponents1(InfoHeaderSection):
    def __init__(self) -> None:
        note = "Suggestions may be approved or denied for any reason at any time."

        super().__init__(
            title       = "Server Suggestions",
            description = "A place to request changes to make the server better for everyone.",
            note        = note,
        )

class SuggestionComponents2(InfoPrimarySection):
    def __init__(self) -> None:
        text = (
            ""
        )

        super().__init__(
            title   = "Suggestions",
            authors = [BOT_OWNER_MENTION],
            text    = text,
        )
