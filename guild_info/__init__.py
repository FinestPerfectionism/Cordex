from bot.ui import LayoutView

from ._base import ensure_views
from .hierarchy import (
    HierarchyComponents1,
    HierarchyComponents2,
    HierarchyComponents3,
    HierarchyComponents4,
    HierarchyComponents5,
)
from .partnerships import PartnershipComponents1, PartnershipComponents2
from .rules import RuleComponents1, RuleComponents2

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
    "PartnershipViewsList",
    "RuleViewsList",
    "ensure_views",
]
