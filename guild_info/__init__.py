from bot.ui import LayoutView

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
from .tickets import TicketComponents

HierarchyViewsList   : list[LayoutView] = [
    HierarchyComponents1(),
    HierarchyComponents2(),
    HierarchyComponents3(),
    HierarchyComponents4(),
    HierarchyComponents5(),
]
PartnershipViewsList : list[LayoutView] = [PartnershipComponents1(), PartnershipComponents2()]
RuleViewsList        : list[LayoutView] = [RuleComponents1(), RuleComponents2()]

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
