from collections.abc import Callable
from operator import eq, ge, gt, le, lt
from typing import Literal

from discord import Member, Role
from discord.app_commands import CheckFailure, check

from bot import Interaction
from core.exceptions import BadEnvironmentGuild
from core.moderation import Actions

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Utilites Base
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# quarantine_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class UnconfiguredQuarantine(CheckFailure):
    pass

def quarantine_cmd[F : Callable[..., object]]() -> Callable[[F], F]:
    async def predicate(interaction : Interaction) -> bool:
        if not interaction.guild:
            raise BadEnvironmentGuild

        actions = Actions(interaction.client, interaction.guild)

        if not await actions.get_quarantine_role():
            raise UnconfiguredQuarantine

        return True

    def decorator(func : F) -> F:
        check(predicate)(func)
        return func

    return decorator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# check_hierarchy
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def check_hierarchy(
    actor      : Member,
    comparison : Literal[">", "<", "=", ">=", "<="],
    target     : Member,
    /,
) -> bool:

    # ⸻ Owner vs Owner

    if actor.guild.owner == actor and target.guild.owner == target:
        return comparison in {"=", ">=", "<="}

    # ⸻ Actor vs Everyone (Actor is Owner)

    if actor.guild.owner == actor:
        return comparison in {">", ">="}

    # ⸻ Everyone vs Owner (Target is Owner)

    if target.guild.owner == target:
        return comparison in {"<", "<="}

    # ⸻ Role vs Role

    actor_role  = actor.top_role
    target_role = target.top_role

    ops : dict[str, Callable[[Role, Role], bool]] = {
        ">"  : gt,
        "<"  : lt,
        "="  : eq,
        ">=" : ge,
        "<=" : le,
    }

    return ops[comparison](actor_role, target_role)
