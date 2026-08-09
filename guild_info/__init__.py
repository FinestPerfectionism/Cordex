from ._base import ensure_views
from .hierarchy import (
    HierarchyComponents1,
    HierarchyComponents2,
    HierarchyComponents3,
    HierarchyComponents4,
    HierarchyComponents5,
)
from .leave import LeaveComponents
from .partnerships import (
    PartnershipComponents1,
    PartnershipComponents2,
    build_partnership_views,
    rebuild_partnership_view,
)
from .rules import RuleComponents1, RuleComponents2
from .suggestions import SuggestionComponents1, SuggestionComponents2
from .tickets import TicketComponents

HierarchyViewsList   = [
    HierarchyComponents1(),
    HierarchyComponents2(),
    HierarchyComponents3(),
    HierarchyComponents4(),
    HierarchyComponents5(),
]
PartnershipViewsList = [PartnershipComponents1(), PartnershipComponents2()]
RuleViewsList        = [RuleComponents1(), RuleComponents2()]
SuggestionViewsList  = [SuggestionComponents1(), SuggestionComponents2()]

__all__ = [
    "HierarchyViewsList",
    "LeaveComponents",
    "PartnershipViewsList",
    "RuleViewsList",
    "TicketComponents",
    "build_partnership_views",
    "ensure_views",
    "rebuild_partnership_view",
]
