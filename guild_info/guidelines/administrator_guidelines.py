from inspect import cleandoc

from discord import SeparatorSpacing
from discord.ui import Container, LayoutView, Separator, TextDisplay


class AdministratorComponents1(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = cleandoc("""
                # Welcome to Administrator Guidelines!\n
                Internal guidelines for the Goobers Administration Team.\n
                -# **Note:** These guidelines are staff-only and may be revised at any time by Directorate decision. Sharing internal administration policy outside staff spaces is prohibited.
                """,
            ),
        ),
    )

class AdministratorComponents2(LayoutView):
    def __init__(
        self,
        timestamp : int,
    ) -> None:
        super().__init__(timeout = None)
        self.container : Container[LayoutView] = Container(
            TextDisplay[LayoutView](
                content = cleandoc(f"""
                    # Administrator Guidelines\n
                    Administrator guidelines last updated <t:{timestamp}:D>.\n
                    -# All below is subject to change at any time based on Directorate decision or structural updates.\n
                    -# Assembled by the Directorate team. Primarily written by <@1311394031640776716>.\n
                    """,
                ),
            ),
            Separator(
                visible = False,
                spacing = SeparatorSpacing.small,
            ),
            Separator(
                visible = True,
                spacing = SeparatorSpacing.small,
            ),
            Separator(
                visible = False,
                spacing = SeparatorSpacing.small,
            ),
            TextDisplay(
                content = cleandoc("""
                    ## §1 Scope and Permissions\n
                    Administrators manage the server's structural and technical infrastructure. Administrators are **not Moderators** — do not take enforcement actions against members. If a moderation situation arises while carrying out administrative duties, defer to the Moderation Team or escalate to a Director.\n\n
                    ### §1.1 Role Scope\n
                    - **Junior Administrators** can manage expressions, manage channels, manage nicknames, and create events.\n
                    - **Senior Administrators** hold all Junior Administrator permissions and additionally manage the guild, manage roles, manage events, manage webhooks, manage bot configurations and integrations, and manage server-level settings.\n
                    - **Directors** hold full administrative authority and may override or reverse any infrastructure change.\n\n
                    ### §1.2 Permission Boundaries\n
                    Administrators must act within the permissions granted to their role. Actions that exceed your role scope must be escalated to a Senior Administrator or Director. Do not request elevated access outside the normal promotion process.\n\n
                    ## §2 Proposal Implementation\n
                    Administrators are responsible for implementing all proposals that have reached Accepted status. Implementation must be carried out accurately and in accordance with the accepted proposand. If the proposand is ambiguous, seek clarification from the proposer or the Staff Committee (or Directorate where applicable) before proceeding.\n\n
                    ### §2.1 NEEDS IMPLEMENTATION\n
                    Once a proposal is accepted, it is tagged NEEDS IMPLEMENTATION. This tag must not be removed until the proposand has been fully carried out. A proposal cannot be locked until implementation is complete.\n\n
                    ### §2.2 Feasibility and NEEDS REVISION\n
                    If a proposand is not technically feasible, cannot be executed with current resources, or requires additional refinement, an Administrator must flag this immediately. The proposal may be placed into NEEDS REVISION, Standstill, or otherwise delayed. Do not silently leave an accepted proposal unimplemented.\n\n
                    ### §2.3 Owner and Director Action Tags\n
                    Some proposals carry OWNER ACTION or S. DIRECTOR ACTION tags, indicating that only the Owner or a Supporting Director can carry out implementation. Do not attempt to implement these independently — flag them to the appropriate party.
                    """,
                ),
            ),
        )
        _ = self.add_item(self.container)

class AdministratorComponents3(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = cleandoc("""
                ## §3 Infrastructure Management\n
                All structural changes to the server must be deliberate and purposeful. Do not make changes that have not been approved through a proposal or explicitly directed by the Directorate. Document all significant changes in the appropriate staff channel after implementation.\n\n
                ### §3.1 Channels\n
                Channel creation, deletion, renaming, or reconfiguration must correspond to an accepted proposal or a direct Directorate instruction. Do not adjust channel permissions, visibility, or structure speculatively.\n\n
                ### §3.2 Roles\n
                Role creation, deletion, or permission changes are Senior Administrator+. Role changes must be sanctioned by the Directorate or correspond to an accepted proposal. Do not modify role permissions speculatively or as a test.\n\n
                ### §3.3 Expressions\n
                Expressions (emojis, stickers, soundboard entries) may be added or removed by Junior and Senior Administrators. Changes must be consistent with server standards and sanctioned by the Directorate or a proposal.\n\n
                ### §3.4 Events\n
                Junior Administrators may create events. Senior Administrators may additionally manage or edit existing events. All events must be sanctioned by the Directorate or correspond to an accepted proposal.\n\n
                ### §3.5 Nicknames\n
                Junior Administrators may manage member nicknames where necessary for structural or organizational purposes. Nickname changes must not be used as an enforcement action — defer to the Moderation Team for anything conduct-related.
                """,
            ),
        ),
    )

class AdministratorComponents4(LayoutView):
    container : Container[LayoutView] = Container(
        TextDisplay(
            content = cleandoc("""
                ## §4 Bot and Integration Management\n
                Bot configuration and integration management is Senior Administrator+. Changes to bot settings, command permissions, or integrations must be sanctioned by the Directorate or an accepted proposal. Document all changes to bot configurations in the appropriate staff channel after implementation.\n\n
                ### §4.1 Webhooks\n
                Webhook xcreation and management is Senior Administrator+. Webhooks must serve a clear structural or operational purpose and must be documented. Unauthorized or unmonitored webhooks must not be created.\n\n
                ### §4.2 Bot Additions and Removals\n
                Adding or removing bots is subject to Directorate review, regardless of proposal status. Proposals involving bot additions are routed directly to Directorate review rather than the standard Staff Committee process. Do not add or remove bots independently.\n\n
                ## §5 Server-Level Settings\n
                Server-level setting changes are Senior Administrator+. This includes verification level, content filters, security configuration, and guild-level feature flags. Changes must be sanctioned by the Directorate. Do not adjust server-level settings speculatively.\n\n
                ### §5.1 Verification and Security\n
                Changes to verification level or security settings that affect the public-facing entry experience must be coordinated with the Directorate and documented after the fact. In raid or disruption events, defer to Directors for lockdown and security decisions — do not adjust security settings independently.\n\n
                ## §6 Administrator Conduct\n
                ### §6.1 Non-Interference with Moderation\n
                Administrators hold no enforcement authority over members. If a moderation situation is observed, report it to the Moderation Team or escalate to a Director — do not act independently.\n\n
                ### §6.2 Permission Abuse\n
                Abusing administrative permissions for personal gain, retaliation, or to bypass server policy is grounds for removal from the Administration Team.\n\n
                ### §6.3 Confidentiality\n
                Do not disclose internal deliberations, internal policy, approved proposal details before implementation, or Directorate directives to non-staff members.\n\n
                ### §6.4 Change Documentation\n
                All significant infrastructure changes must be noted in the appropriate staff channel after implementation. This gives the team a clear record of what changed and why.\n\n
                ### §6.5 Reviewability\n
                All administrative actions are reviewable by the Directorate. Be accurate and deliberate — undocumented or unexplained changes reduce review quality and may be reversed.\n\n
                ## §7 Expectations and Coordination\n
                ### §7.1 Activity\n
                Administrators are expected to remain reasonably active and responsive to implementation tasks. Prolonged inactivity without prior notice may result in removal from the Administration Team at Directorate discretion.\n\n
                ### §7.2 Communication\n
                Communicate openly with the team when undertaking significant infrastructure changes. Note ongoing work in the appropriate staff channel to avoid duplicate or conflicting actions.\n\n
                ### §7.3 Coordination with the Directorate\n
                Administrators operate under the direction of the Directorate. When in doubt about the scope or intent of an instruction, seek clarification before acting. Do not interpret broad directives speculatively — precision matters in infrastructure changes.\n\n
                ### §7.4 Coordination with the Moderation Team\n
                When an infrastructure change may affect moderation workflows — such as modifying ticket channels, alert channels, or bot command access — notify the Moderation Team in advance where practical. Changes that disrupt active moderation operations without prior notice are disruptive and should be avoided.\n\n
                ### §7.5 Rollback and Errors\n
                If a change produces an unintended result, report it to the Directorate immediately and document what changed and what went wrong. Do not silently correct mistakes through further undocumented changes. Transparency in errors is expected and will not be penalized unless the error resulted from negligence or acting outside authorized scope.
                """,
            ),
        ),
    )
