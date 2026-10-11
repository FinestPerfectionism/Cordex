from discord.utils import escape_markdown, format_dt

from core.moderation import Case

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Case Commands Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


def format_summary(case : Case) -> str:
    subjects : list[str] = []

    if case.target is not None:
        subjects.append(case.target.mention)
    if case.channel is not None:
        subjects.append(case.channel.mention)
    if not subjects:
        subjects.append("Unknown Member")

    subjects.append(case.moderator.mention)

    lines = [
        f"## {case.action_type.readable()}",
        f"**{" | ".join(subjects)}**",
        f"*{escape_markdown(case.reason)}*",
    ]

    if case.purge_amount is not None:
        forced = ", forced" if case.purge_force else ""
        lines.append(f"-# Purged {case.purge_amount} messages{forced}.")

    lines.extend((f"-# Occurred at {format_dt(case.created_at, "F")}, {format_dt(case.created_at, "R")}.", f"-# Case ID: #{case.id}"))

    return "\n".join(lines)
