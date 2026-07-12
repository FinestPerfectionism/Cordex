from discord.utils import utcnow

from constants import TICKETS_CHANNEL_ID

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
    def __init__(self) -> None:
        text = (
            "## §1 Eligibility\n"
            "To be considered for partnership, a server must:\n\n"
            "- Comply fully with Discord Terms of Service. (Click the button above to see them)\n"
            "- Maintain a clear and publicly accessible ruleset.\n"
            "- Have an active and identifiable moderation team.\n"
            "- Demonstrate consistent member activity and structural stability.\n"
            "- Not primarily distribute NSFW content. (NSFW channels are fine, please make sure they are not accessible to minors)\n"
            "- Not engage in harassment, discrimination, doxxing, impersonation, or organized disruption.\n"
            "- Have a fully eligible server description with an acceptable usage of unicode characters.\n\n"
            "Servers failing to meet these standards will not be considered.\n\n"
            "## §2 Request Procedure\n"
            "### §2.1 Ticket Requirement\n"
            "All partnership requests must be initiated through the official tickets system.\n\n"
           f"- Go to <#{TICKETS_CHANNEL_ID}>.\n"
            "- Open a ticket directed to the **Directors**. Moderators recieving partnership requests should escalate the ticket to directors using `.escalate`.\n"
            "- Please provide your:\n"
            "  - Server name\n"
            "  - Server invite link\n"
            "  - Member count\n"
            "  - Brief description of the server\n"
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
            "A partnership may be revoked at any time if any of the standards of eligbility above are no longer present\n\n"
            "## §5 Authority\n"
            "All partnership decisions are made solely by the Directorate.\n"
            "No other staff member or role may or can approve partnerships. Do not harrass staff about your partnership.\n"
        )

        super().__init__(
            title     = "Partnership Requirements",
            text      = text,
            timestamp = utcnow(),
            authors   = ["<@1311394031640776716>"],
            button    = TOSButton(),
        )
