from ._base import InfoHeaderSection, InfoPrimarySection, InfoSecondarySection

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Hierarchy Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class HierarchyComponents1(InfoHeaderSection):
    def __init__(self) -> None:
        note = (
            "Roles and their responsibilities are subject to change at any time based on Directorate decision or structural updates. Sensitive information such as internal policy and nomination details has not been shared here"
        )

        super().__init__(
            title       = "the Hierarchy",
            description = "The hierarchy of the server",
            note        = note,
        )

class HierarchyComponents2(InfoPrimarySection):
    def __init__(self) -> None:
        text = (
            "## Goobers Directorate\n"
            "The **Goobers Directorate** oversees the entire server and holds the highest level of authority. Directors are responsible for governance, internal staff policy, and high-level decision making. While Directors are typically occupied with backend responsibilities, they hold Senior Staff status within both the Moderation and Administration Teams and are expected to intervene in escalated situations when necessary.\n\n"
            "**Responsibilities**\n"
            "- Establish and maintain internal policies affecting staff operations.\n"
            "- Oversee external policies affecting the public, which are carried out by Administrators.\n"
            "- Appoint members to major staff bodies and promote qualified staff into senior positions.\n"
            "- Review and decide on all partnership requests.\n"
            "- Handle ban appeals and escalated moderation cases.\n"
            "- Manage and resolve quarantined members.\n\n"
            "**Moderation Permissions**\n"
            "Directors hold full moderation permissions, including the ability to kick, ban, unban, timeout, and quarantine members. These permissions are exercised primarily in escalated or exceptional circumstances.\n\n"
            "> Directors are **very rarely nominated** and are chosen only under special circumstances.\n\n"
            "### Leading Director\n"
            "The **Leading Director** is the true owner of the server and holds ultimate authority over all guild operations and governance decisions. No decision may override the Leading Director's determination.\n\n"
            "> This position is **not obtainable**.\n\n"
            "### Supporting Directors\n"
            "**Supporting Directors** assist in governance and high-level decision making alongside the Leading Director. They are expected to hold Senior Staff status in both the Moderation and Administration Teams.\n\n"
            "**Requirements**\n"
            "- Must hold **Senior Staff status** within both the Moderation Team and the Administration Team.\n"
            "> This position is obtainable only through **appointment by the existing Directorate**."
        )

        super().__init__(
            title   = "Hiearchy",
            authors = ["<@1311394031640776716>", "<@1167207694424350740>", "<@1135600413954019339>", "<1484920400767877161>"],
            text    = text,
        )

class HierarchyComponents3(InfoSecondarySection):
    def __init__(self) -> None:
        super().__init__(
            text = (
                "## Goobers Administration Team\n"
                "The **Administration Team** is responsible for managing the server's structure and maintaining public-facing policies as directed by the Directorate. Administrators implement approved suggestions and oversee the server's technical infrastructure. The Administration Team is **not the same as the Moderation Team**, though staff may exist within both.\n\n"
                "**Primary Responsibilities**\n"
                "- Implement approved suggestions.\n"
                "- Maintain server infrastructure, including channels, roles, events, expressions, and configuration.\n"
                "- Manage bot configurations and integrations.\n"
                "- Manage server-level settings such as verification level and security configuration.\n"
                "- Carry out external policies as directed by the Directorate.\n\n"
                "### Senior Administrators\n"
                "**Senior Administrators** hold all Junior Administrator permissions and are additionally responsible for expanded infrastructure management, including bot and integration oversight and server-level settings.\n\n"
                "> Promotion is granted through **appointment by the Directorate**.\n\n"
                "### Junior Administrators\n"
                "**Junior Administrators** assist with routine structural maintenance under the direction of Senior Administrators and the Directorate.\n\n"
                "> This position is obtained through a **successful nomination**.\n\n"
                "## Goobers Moderation Team\n"
                "The **Moderation Team** enforces server rules, manages reports and tickets, and ensures community standards are upheld. The Moderation Team is **not the same as the Administration Team**, though staff may exist within both.\n\n"
                "**Ticket System**\n"
                "The server operates a two-track ticket system. **Moderator tickets** handle questions and issues involving members. **Director tickets** handle partnership requests and issues involving staff. All Moderators are expected to handle tickets within their scope and escalate out-of-scope tickets to Directors using `.escalate`.\n\n"
                "### Senior Moderators\n"
                "**Senior Moderators** hold all Junior Moderator permissions and are additionally authorized to take stronger enforcement action. Senior Moderators are expected to assist Junior Moderators upon request or when a situation proves difficult to manage.\n\n"
                "> Promotion is granted through **appointment by the Directorate**.\n\n"
                "### Junior Moderators\n"
                "**Junior Moderators** assist with routine moderation tasks and handle tickets, escalating to director tickets when a ticket falls outside their scope or becomes difficult to manage.\n\n"
                "> This position is obtained through a **successful nomination**.\n\n"
            ),
        )

class HierarchyComponents4(InfoSecondarySection):
    def __init__(self) -> None:
        super().__init__(
            text = (
                "## Goobers Staff Team\n"
                "The **Goobers Staff Team** consists of members within the **Moderation Team**, the **Administration Team**, or both. Staff members assist with maintaining the community. Staff members may hold positions in both teams simultaneously.\n\n"
                "Staff membership may be obtained through:\n"
                "- Partnerships.\n"
                "- Joining the **Moderation Team** or **Administration Team**."
            ),
        )

class HierarchyComponents5(InfoSecondarySection):
    def __init__(self) -> None:
        super().__init__(
            text = (
                "## Honourable\n"
                "**Hounourables** are community members who have demonstrated a level of trust and engagement within the server.\n\n"
                "Honourables are not Staff, but are a recognized contributor group within the community. Members holding this role are more likely to be considered for nomination to the Moderation Team or Administration Team.\n\n"
                "> This role is obtainable through **nomination**."
            ),
        )
