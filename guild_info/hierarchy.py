from typing import Self
from discord.ui import Container, LayoutView, TextDisplay

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Hierarchy Information
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class HierarchyComponents1(LayoutView):
    container : Container[Self] = Container(
        TextDisplay(
            content = (
                "# Welcome to the Hierarchy!\n"
                "The hierarchy of the server.\n"
                "-# **Note:** Roles and their responsibilities are subject to change at any time based on Directorate decision or structural updates. Sensitive information such as internal policy and nomination details has not been shared here."
            ),
        ),
    )

class HierarchyComponents2(LayoutView):
    def __init__(self, timestamp : int) -> None:
        super().__init__(timeout = None)
        self.add_item(
            Container(
                TextDisplay(
                    content = (
                        "# Hierarchy\n"
                       f"Hierarchy last updated <t:{timestamp}:D>.\n"
                        "-# All below is subject to change at any time based on Directorate decision or structural updates.\n"
                        "-# Assembled by the Directorate team. Primarily written by <@1311394031640776716>; assisted by <@1167207694424350740>, <@1135600413954019339>, and <@1333839098485542949>.\n"
                    ),
                ),
                HiddenSmallSeparator(),
                VisibleSmallSeparator(),
                HiddenSmallSeparator(),
                TextDisplay(
                    content = (
                        "## Goobers Directorate\n"
                        "The **Goobers Directorate** oversees the entire server and holds the highest level of authority. Directors are responsible for governance, internal staff policy, and high-level decision making. While Directors are typically occupied with backend responsibilities, they hold Senior Staff status within both the Moderation and Administration Teams and are expected to intervene in escalated situations when necessary.\n\n"
                        "**Responsibilities**\n"
                        "- Establish and maintain internal policies affecting staff operations.\n"
                        "- Oversee external policies affecting the public, which are carried out by Administrators.\n"
                        "- Review and decide on escalated proposals from the Staff Committee.\n"
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
                        "**Supporting Directors** assist in governance and high-level decision making alongside the Leading Director. They are active participants in the Staff Committee and are expected to hold Senior Staff status in both the Moderation and Administration Teams.\n\n"
                        "**Requirements**\n"
                        "- Must hold **Senior Staff status** within both the Moderation Team and the Administration Team.\n"
                        "- Must be an active member of the **Staff Committee**.\n\n"
                        "> This position is obtainable only through **appointment by the existing Directorate**."
                    ),
                ),
            ),
        )

class HierarchyComponents3(LayoutView):
    container : Container[Self] = Container(
        TextDisplay(
            content = (
                "## Staff Committee\n"
                "The **Staff Committee** is the final decision-making body for Staff Proposals. It is composed of all active Directors and the Owner. After an advisory poll concludes, the committee reviews all vote data, staff discussion, and operational considerations before issuing a binding decision.\n\n"
                "For full details on the Staff Committee's composition, procedures, voting thresholds, and review timelines, refer to the staff proposal information.\n\n"
                "> This position is obtainable through **appointment by the Directorate**."
            ),
        ),
    )

class HierarchyComponents4(LayoutView):
    container : Container[Self] = Container(
        TextDisplay(
            content = (
                "## Goobers Administration Team\n"
                "The **Administration Team** is responsible for managing the server's structure and maintaining public-facing policies as directed by the Directorate. Administrators implement approved proposals and oversee the server's technical infrastructure. The Administration Team is **not the same as the Moderation Team**, though staff may exist within both.\n\n"
                "**Primary Responsibilities**\n"
                "- Implement approved Staff Proposals.\n"
                "- Maintain server infrastructure, including channels, roles, events, expressions, and configuration.\n"
                "- Manage bot configurations and integrations.\n"
                "- Manage server-level settings such as verification level and security configuration.\n"
                "- Carry out external policies as directed by the Directorate.\n\n"
                "### Senior Administrators\n"
                "**Senior Administrators** hold all Junior Administrator permissions and are additionally responsible for expanded infrastructure management, including bot and integration oversight and server-level settings.\n\n"
                "**Permissions**\n"
                "- Manage the guild.\n"
                "- Manage roles.\n"
                "- Manage events.\n"
                "- Manage webhooks.\n"
                "- Create expressions.\n"
                "- Manage bot configurations and integrations.\n"
                "- Manage server-level settings.\n\n"
                "> Promotion is granted through **appointment by the Directorate**.\n\n"
                "### Junior Administrators\n"
                "**Junior Administrators** assist with routine structural maintenance under the direction of Senior Administrators and the Directorate.\n\n"
                "**Permissions**\n"
                "- Manage expressions.\n"
                "- Manage channels.\n"
                "- Manage nicknames.\n"
                "- Create events.\n\n"
                "> This position is obtained through a **successful application**. Applications are not always open.\n\n"
                "## Goobers Moderation Team\n"
                "The **Moderation Team** enforces server rules, manages reports and tickets, and ensures community standards are upheld. The Moderation Team is **not the same as the Administration Team**, though staff may exist within both.\n\n"
                "**Ticket System**\n"
                "The server operates a two-track ticket system. **Moderator tickets** handle questions and issues involving members. **Director tickets** handle partnership requests and issues involving staff. All Moderators are expected to handle tickets within their scope and escalate out-of-scope tickets to Directors using `.escalate`.\n\n"
                "### Senior Moderators\n"
                "**Senior Moderators** hold all Junior Moderator permissions and are additionally authorized to take stronger enforcement action. Senior Moderators are expected to assist Junior Moderators upon request or when a situation proves difficult to manage.\n\n"
                "**Additional Permissions**\n"
                "- Quarantine members.\n"
                "- Kick members.\n"
                "- Ban members.\n\n"
                "> Promotion is granted through **appointment by the Directorate**.\n\n"
                "### Junior Moderators\n"
                "**Junior Moderators** assist with routine moderation tasks and handle tickets, escalating to director tickets when a ticket falls outside their scope or becomes difficult to manage.\n\n"
                "**Permissions**\n"
                "- Create moderation notes.\n"
                "- View moderation notes.\n"
                "- Mute members.\n\n"
                "> This position is obtained through a **successful application**. Applications are not always open."
            ),
        ),
    )

class HierarchyComponents5(LayoutView):
    container : Container[Self] = Container(
        TextDisplay(
            content = (
                "## Goobers Staff Team\n"
                "The **Goobers Staff Team** consists of members within the **Moderation Team**, the **Administration Team**, or both. Staff members assist with maintaining the community and may submit and vote on proposals intended to improve server operations. Staff members may hold positions in both teams simultaneously.\n\n"
                "Staff membership may be obtained through:\n"
                "- Partnerships.\n"
                "- Appointment to the **Staff Committee**.\n"
                "- Joining the **Moderation Team** or **Administration Team**."
            ),
        ),
    )

class HierarchyComponents6(LayoutView):
    container : Container[Self] = Container(
        TextDisplay(
            content = (
                "## Guild Trustees\n"
                "**Guild Trustees** are community members who have demonstrated a level of trust and engagement within the server. They may raise Staff Proposals to suggest improvements, changes, or additions to the server. All proposands are expected to be formal, precise, and beneficial to the server's growth and function.\n\n"
                "Guild Trustees are not Staff, but are a recognized contributor group within the community. Members holding this role are more likely to be considered for nomination to the Moderation Team, Administration Team, or Staff Committee.\n\n"
                "For full details on what Guild Trustees may and may not propose, refer to the staff proposal information.\n\n"
                "> This role is obtainable through **nomination**."
            ),
        ),
    )

class HierarchyComponents7(LayoutView):
    container : Container[Self] = Container(
        TextDisplay(
            content = (
                "## Verified\n"
                "The **Verified** role is granted upon passing the server's entry verification. It serves as an anti-raid gate and is required to gain access to the server's channels.\n\n"
                "> This role is obtained automatically upon **completing server verification**."
            ),
        ),
    )
