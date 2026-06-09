# ruff: noqa: E501

from inspect import cleandoc

from discord.ui import (
    ActionRow,
    Button,
    Container,
    LayoutView,
    TextDisplay,
)
from typing_extensions import override

from core.utilities import (
    VisibleLargeSeparator,
    VisibleSmallSeparator,
    blurple,
    green,
    red,
)

from bot import Interaction


class AdministratorsRolesComponents(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay[LayoutView](
            content = cleandoc(
                """
                # Goobers Administration Team\n
                The Goobers Administration Team is responsible for overseeing server management and ensuring that all approved structural or operational changes are properly carried out.\n\n
                **Tasks**\n
                > *To implement proposals raised by Staff that have reached Accepted status.*\n\n
                When a proposal is accepted, an Administrator(s) is expected to implement its proposand. If a proposand is not technically feasible, cannot be executed with current resources, or requires additional refinement, Administrators may place the proposal into Needs Revision, Standstill, or otherwise delay implementation until it becomes feasible.
                """,
            ),
        ),
        VisibleLargeSeparator(),
        TextDisplay("-# **Note:** Administrators are held under the same rules and are expected to also do the same jobs as guild Trustees *and* Moderators. No exceptions."),
        accent_color = 0xff8cd5,
    )

class ModeratorsRolesComponents(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay[LayoutView](
            content = (
                "# Goobers Moderation Team\n"
                "The Goobers Moderation Team is responsible for overseeing rule enforcement, maintaining community safety, and supporting the server's overall stability.\n\n"
                "**Tasks**\n"
                "> *To vote on and raise proposals that improve The Goobers server and its community.*\n\n"
                "All Moderators may raise Staff Proposals and vote on them. Senior Moderators+ may assist in directing or reviewing proposands for clarity or practicality. All proposands are expected to be formal, precise, and beneficial to the server's growth and function."
            ),
        ),
        VisibleLargeSeparator(),
        TextDisplay(
            content =
                "-# **Note:** Moderators are held under the same rules and are expected to also do the same jobs as guild Trustees. No exceptions.",
        ),
        accent_color = 0x87e9ff,
    )

class TrusteeRolesComponents(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = (
                "# Goobers Guild Trustees\n"
                "Guild Trustees are members of the community who contribute to the server's improvement through proposals and suggestions.\n\n"
                "**Tasks**\n"
                "> *To raise proposals that improve The Goobers server and its community.*\n\n"
                "Guild Trustees may raise Staff Proposals to suggest improvements, changes, or additions to the server. All proposands are expected to be formal, precise, and beneficial to the server's growth and function."
            ),
        ),
        accent_color = 0xfacd6c,
    )

class CommitteeRolesComponents(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = (
                "# Goobers Staff Committee\n"
                "The Staff Committee is the final decision-making body for Staff Proposals. After the advisory poll period concludes, the committee reviews all vote data, staff discussion, and operational considerations before issuing a binding decision.\n\n"
                "**Tasks**\n"
                "> *To review advisory poll results and issue final decisions on Staff Proposals.*\n\n"
                "The Staff Committee may Accept, Accept with minor revisions, Request revision, Deny, or place a proposal into Standstill. When acting contrary to strong staff consensus, the committee is expected to provide brief reasoning for their decision."
            ),
        ),
        accent_color = 0xf9a56b,
    )

class AdministratorsRoles(Button[LayoutView]):
    def __init__(self) -> None:
        super().__init__(
            style     = green,
            label     = "Administrator's Roles",
            custom_id = "persistent_administrator_button",
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        _ = await interaction.response.send_message(
            view      = AdministratorsRolesComponents(),
            ephemeral = True,
        )

class ModeratorsRoles(Button[LayoutView]):
    def __init__(self) -> None:
        super().__init__(
            style     = green,
            label     = "Moderator's Roles",
            custom_id = "persistent_moderator_button",
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        _ = await interaction.response.send_message(
            view      = ModeratorsRolesComponents(),
            ephemeral = True,
        )

class TrusteeRoles(Button[LayoutView]):
    def __init__(self) -> None:
        super().__init__(
            style     = blurple,
            label     = "Trustee's Roles",
            custom_id = "persistent_trustee_button",
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        _ = await interaction.response.send_message(
            view      = TrusteeRolesComponents(),
            ephemeral = True,
        )

class CommitteeRoles(Button[LayoutView]):
    def __init__(self) -> None:
        super().__init__(
            style     = red,
            label     = "Committee's Roles",
            custom_id = "persistent_committee_button",
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        _ = await interaction.response.send_message(
            view      = CommitteeRolesComponents(),
            ephemeral = True,
        )

class StaffProposalComponents1(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = (
                "# Welcome to Staff Proposals!\n"
                "A branch of the server dedicated to making improvements to the server that will benefit the community and its members."
            ),
        ),
    )

class StaffProposalComponents2a(LayoutView):
    def __init__(self, timestamp : int) -> None:
        super().__init__(timeout = None)
        self.container : Container[LayoutView] = Container(
            TextDisplay(
                content = (
                    "# Staff Proposal Information\n"
                    f"Staff proposals last updated <t:{timestamp}:D>.\n"
                    "-# All below is subject to change at any time based on Directorate decision or structural updates.\n"
                    "-# Assembled by the Directorate team. Primarily written by <@1311394031640776716>."
                ),
            ),
            VisibleSmallSeparator(),
            VisibleSmallSeparator(),
            VisibleSmallSeparator(),
            TextDisplay(
                content = (
                    "Any member of the **Goobers Staff Team** (Administrators + Moderators + Directors + Owner) is allowed to vote in a proposal, or raise a proposal. All proposals are expected to be beneficial to the Goobers and its community.\n"
                    "## Important Information\n"
                    "### Advisory Votes\n"
                    "Staff Proposal polls are **non-binding advisory votes**. Poll results are visible and recorded, but do not automatically Accept or Deny a proposal. Final decision authority rests with the **Staff Committee**.\n"
                    "### Abstaining\n"
                    "Abstentions are recorded as part of the advisory poll. They are not counted toward any threshold and are reviewed by the Staff Committee alongside all other vote data.\n"
                    "### Staff Count\n"
                    "Vote totals are tracked for advisory reference during the poll period.\n"
                    "- **S** = number of Staff voting roles.\n"
                    "- **Majority** = ⌈(S / 2) + 1⌉.\n"
                    "This is used as an advisory reference only and does not determine the proposal's outcome.\n"
                    "### Inactive or Missing Votes\n"
                    "If a proposal's poll expires with missing Staff votes, it proceeds to the Staff Committee as-is with whatever vote data was collected.\n"
                    "### Vote Changes\n"
                    "- Staff may change their votes at any time before the poll ends.\n"
                    "- Once the poll expires, votes are locked for the record."
                ),
            ),
            TextDisplay(
                content = (
                    "## Staff Groups\n"
                    "**Staff** consists of:\n"
                    "- **Owner**\n"
                    "- **Directors**\n"
                    "- **Administrators**\n"
                    "- **Moderators**\n"
                    "All Staff are equal in advisory voting ability. Administrators are responsible for implementing accepted proposals.\n"
                    "## Poll Format\n"
                    "**Motion.**\n"
                    "- <:cgreen:1437171496857501889> Accept  \n"
                    "- <:cblue:1437171597952811059> Abstain  \n"
                    "- <:cred:1437171288631414966> Deny  \n"
                    "- <:cyellow:1437171198982357073> Accept, with minor revisions (optional)\n"
                    "Poll length must be **three days or longer** if a proposand demands it.\n"
                    "## Vetos\n"
                    "- **Director Veto:** Any staff member with the Director role may veto a proposal at any time. This veto is absolute and does not require consultation or approval from other Directors or Staff members.  \n"
                    "- **Veto Scope:** A veto can be applied to any proposal, regardless of its current vote count or status.  \n"
                    "- **Veto Effect:** Once a veto is issued, the proposal is immediately halted and considered denied. Directors may either ask for revision, or end the proposal outright.\n"
                    "## Scope\n"
                    "While a user could conceivably raise a proposal about anything, Staff are not empowered to make any change they like in staff-proposals. Below is a non-exhaustive list of the types of suggestions that will *not* be considered:\n"
                    "- Suggestions that relate to moderator policies or actions such as timeouts or bans.\n"
                    "  - Staff may request policy changes if majority (75%) of staff agree on the change. This update may *not* be raised in staff-proposals.\n"
                    "- Suggestions pertaining to individual users.\n"
                    "- Suggestions that relate to the core rules and guiding philosophy of the server.\n"
                    "  - Staff may request rule changes if *all* (100%) of staff agree on the change. The update may *not* be raised in staff-proposals.\n"
                    "- Suggestions that relate to updates of staff-proposal-info.\n"
                    "Staff may make suggestions to the items listed above __in the appropriate channel__, such as <#1444452435006590996>, <#1386133249373376665>, or <#1436345318554996976>.\n"
                    "Guild Trustees may *not* suggest the items listed above anywhere in the server. \n\n"
                    "-# **Proposand:** the core idea of a raised proposal.\n"
                    "-# **Guild Trustees:** those with the <@&1463694813525180477> role."
                ),
            ),
            VisibleLargeSeparator(),
            ActionRow(
                AdministratorsRoles(),
                ModeratorsRoles(),
                CommitteeRoles(),
                TrusteeRoles(),
            ),
        )
        _ = self.add_item(self.container)

class StaffProposalComponents2b(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = (
                "## Proposal Review\n"
                "### Staff Committee\n"
                "After the advisory poll concludes, the **Staff Committee** reviews the proposal. The committee considers vote totals, staff discussion, technical feasibility, and operational concerns before issuing a final decision.\n"
                "The Staff Committee may:\n"
                "- **Accept**\n"
                "- **Accept with minor revisions**\n"
                "- **Request revision**\n"
                "- **Deny**\n"
                "- **Place in Standstill**\n"
                "When acting contrary to strong staff consensus, the committee should provide brief reasoning for their decision.\n"
                "### Composition\n"
                "The Staff Committee is composed of all active Directors and the Owner. A quorum of at least two committee members is required to issue any final decision.\n"
                "### Appointment & Removal\n"
                "Committee membership is tied to the Director and Senior Staff groups. Nominations are casted by directors.\n"
                "### Internal Voting Threshold\n"
                "A simple majority of present committee members is sufficient to issue Accept, Accept with minor revisions, or Deny decisions. Standstill and Contested status require unanimous agreement among present members.\n"
                "### Review Timelines\n"
                "The Staff Committee must issue a final decision within **5 days** of the advisory poll concluding. If no decision is reached within this window, the proposal automatically enters Contested status.\n"
                "### Interaction with Vetos\n"
                "Director veto powers operate independently of the Staff Committee review process. A veto may be exercised at any point before the committee issues a final decision. Once a final decision has been issued, veto powers may not be retroactively applied.\n"
                "## Directorate Review\n"
                "Certain proposals are not subject to the standard Staff Committee process and are instead passed directly to the **Directorate** for review. This applies to specific circumstances where the nature of the proposal falls outside the scope of staff advisory voting, such as the addition of bots to the server.\n"
                "When a proposal is referred to the Directorate:\n"
                "- The Directorate reviews the proposal internally and issues a decision at their discretion.\n"
                "- Normal veto, revision, and standstill mechanics still apply within Directorate review.\n"
                "Staff may still provide input or reasoning in the proposal thread, but the final decision rests entirely with the Directorate.\n"
                "## Proposal Format\n"
                "All proposals passed for review must follow the format below. Proposals that do not conform to this format will automatically be back-passed for revisions.\n\n"
                "```\n"
                "# {title}\n"
                "## Details\n"
                "- DD/MM/YY\n"
                "- {proposer}\n"
                "## Proposand Details\n"
                "### Proposand\n"
                "> The wanted desired outcome of the proposal.\n"
                "### Reasons\n"
                "> Why the proposand should be accepted.\n"
                "### Additional Notes\n"
                "> Any additional notes.\n"
                "```"
            ),
        ),
    )

class StaffProposalComponents3(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = (
                "# Proposal Accepted\n"
                "A proposal is Accepted when the Staff Committee issues an Accept decision after reviewing the advisory poll and associated discussion.\n"
                "## Acceptance\n"
                "The Staff Committee may Accept a proposal if:\n"
                "- The advisory vote reflects sufficient staff support.\n"
                "- The proposand is technically feasible and sufficiently specified.\n"
                "- No unresolved operational or policy concerns remain.\n"
                "The committee may also **Accept with minor revisions**, in which case Administrators implement the proposand with the noted adjustments.\n"
                "### Implementation\n"
                "Administrators implement all accepted proposals. If the proposal requires the Owner or Supporting Director specifically, the relevant tag is used.\n"
                "# Proposal Contested\n"
                "A proposal is Contested when the Staff Committee determines that the advisory vote and discussion do not produce a clear or actionable outcome.\n"
                "## Contested Conditions\n"
                "The Staff Committee may place a proposal into Contested if:\n"
                "- Advisory votes are closely divided with no clear signal.\n"
                "- Staff discussion raises significant unresolved disagreements.\n"
                "- The committee requires additional input before issuing a final decision.\n"
                "### Contested Period\n"
                "A **3-day discussion period** begins.\n"
                "- Staff may revise their advisory votes.\n"
                "- Staff may provide additional reasoning or objections.\n"
                "- If the committee reaches a decision during this period, the proposal resolves immediately.\n"
                "### After 3 Days\n"
                "If the committee still cannot reach a decision:\n"
                "- The **Owner** issues a final deciding determination.\n"
                "- The Owner's decision determines Accepted or Denied.\n"
                "The Owner may not override a clear Staff Committee decision at any time.\n"
                "# Proposal Denied\n"
                "A proposal is Denied when the Staff Committee issues a Deny decision after reviewing the advisory poll and associated discussion.\n"
                "## Denial\n"
                "The Staff Committee may Deny a proposal if:\n"
                "- The advisory vote reflects insufficient staff support.\n"
                "- The proposand is technically infeasible or insufficiently specified.\n"
                "- Operational, policy, or structural concerns cannot be resolved.\n"
                "# Proposal Standstill\n"
                "The **Standstill** status is used only for rare, special circumstances. This status is not triggered automatically and must be entered manually by the Staff Committee.\n"
                "## Standstill Conditions\n"
                "A proposal may enter Standstill if:\n"
                "- Motion and votes conflict severely.\n"
                "- Staff statements contradict each other.\n"
                "- The proposal becomes halted for administrative, technical, or logistical reasons.\n"
                "- The situation is too mixed to evaluate.\n"
                "- The Staff Committee explicitly determines that normal evaluation cannot proceed.\n"
                "A proposal must exit Standstill before any final status (Accepted, Contested, Denied) is applied."
            ),
        ),
    )

class StaffProposalComponents4(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = cleandoc(
                """
                # Non-Status Tags\n
                ## NEEDS REVISION\n
                Used when a proposal receives positive motion, but Administrator(s) state implementation is not possible in its current form, or, when Directors veto a proposal and the original poster chooses to rewrite.\n
                **Rules:**\n
                - A proposal **cannot be locked** while marked Needs Revision.\n
                - OP must revise the proposand.\n
                - After revision, the proposal restarts evaluation.\n
                ## NEEDS IMPLEMENTATION\n
                Used only **after** a proposal is accepted.\n
                **Rules:**\
                - A proposal **cannot be locked** until Administrators implement the proposand.\n
                - Tag is removed once implementation is complete.\n
                ## OWNER ACTION\n
                Used for cases where:\n
                - Only the Owner can implement a proposal's requirements.\n
                Does not affect vote mechanics.\n
                ## S. DIRECTOR ACTION\n
                Used for cases where:\n
                - Only a Supporting Director can implement a proposal's requirements.\n
                Does not affect vote mechanics.\n
                ## LOCKED\nA proposal is **Locked** when:\n
                - Its result is final **and**\n
                - The proposand has been implemented.\n
                Staff may still send messages, but a Locked proposal shouldn't be changed or reopened unless more discussion on the topic is necessary or new issues have arisen.
                """,
            ),
        ),
    )
