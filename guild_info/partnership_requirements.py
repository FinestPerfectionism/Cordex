from datetime import datetime
from constants import TICKET_CHANNEL_ID
from ._base import InfoHeaderSection, InfoPrimarySection, TOSButton

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Partnership Requirements Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class RequirementComponents1(InfoHeaderSection):
    def __init__(self) -> None:
        super().__init__(
            title       = "our Partnership Requirements",
            description = "Our requirements for server partnerships",
            note        = "It is within Directors' discretion as to whether we choose to partner wtih your server regardless of if the rules they find you to be not qualifying for are listed here. Directors are not required to provide a reason, if any, when denying a partnerhsip",
        )

class RequirementComponents2(InfoPrimarySection):
    def __init__(self, timestamp : datetime) -> None:
        text = (
            "## §1 Eligibility\n"
            "To be considered for partnership, a server must:\n\n"
            "- Comply fully with Discord Terms of Service.\n"
            "- Maintain a clear and publicly accessible ruleset.\n"
            "- Have an active and identifiable moderation team.\n"
            "- Demonstrate consistent member activity and structural stability.\n"
            "- Not primarily distribute NSFW content.\n"
            "- Not engage in harassment, discrimination, doxxing, impersonation, or organized disruption.\n\n"
            "Servers failing to meet these standards will not be considered. No exceptions.\n\n"
            "## §2 Request Procedure\n"
            "### §2.1 Ticket Requirement\n"
            "All partnership requests must be initiated through the official tickets system.\n\n"
           f"- Go to <#{TICKET_CHANNEL_ID}>.\n"
            "- Open a ticket directed to the **Directors**. Moderators recieving partnership requests should escalate the ticket to directors using `.escalate`.\n"
            "- Clearly provide:\n"
            "  - Server name\n"
            "  - Server invite link\n"
            "  - Member count\n"
            "  - Brief description of the server\n"
            "  - Explanation of why a partnership would be mutually beneficial\n\n"
            "Requests made outside the tickets system will not be reviewed.\n\n"
            "### §2.2 Review\n"
            "- Directors review all partnership tickets internally.\n"
            "- Additional information may be requested during review.\n"
            "- Decisions are issued at Directorate discretion.\n\n"
            "There is no public advisory vote for partnership requests.\n\n"
            "## §3 Approval & Implementation\n"
            "If approved:\n\n"
            "- Terms of partnership will be communicated within the ticket.\n"
            "- Advertisement placement or announcement format will be specified by Directors.\n"
            "- Implementation is handled internally by authorized staff.\n\n"
            "## §4 Termination\n"
            "A partnership may be revoked at any time if:\n\n"
            "- The partner server violates Discord policy.\n"
            "- The partner server violates The Goobers' standards of conduct.\n"
            "- The partner becomes inactive or structurally unstable.\n"
            "- The Directorate determines continued association is not in the server's interest.\n\n"
            "Revocation does not require public justification.\n\n"
            "## §5 Authority\n"
            "All partnership decisions are made solely by the Directorate.\n"
            "No other staff member or role may independently approve, promise, or negotiate a partnership.\n"
        )

        super().__init__(
            title     = "Partnership Requirements",
            text      = text,
            timestamp = timestamp,
            authors   = ["<@1311394031640776716>"],
            button    = TOSButton(),
        )
