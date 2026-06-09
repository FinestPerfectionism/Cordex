from collections.abc import Callable, Coroutine
from typing import Protocol, cast

import discord
from discord import app_commands
from discord.ext import commands

from bot import CtxOrInteraction
from constants import (
    ADMINISTRATORS_ROLE_ID,
    BOT_OWNER_ID,
    DIRECTORS_ROLE_ID,
    MODERATORS_ROLE_ID,
    SENIOR_ADMINISTRATORS_ROLE_ID,
    SENIOR_MODERATORS_ROLE_ID,
    STAFF_ROLE_ID,
)
from core import exceptions as e

from .help import (
    AccessData,
    AccessNode,
    ChannelRestriction,
    P,
    RoleNode,
    T_co,
    UserNode,
    evaluate_access,
    get_access_data,
    resolve_member,
)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Permissions Management
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

class AccessControlled(Protocol):
    __access_data__ : AccessData

CommandCallback = Callable[P, Coroutine[None, None, T_co]]

async def access_predicate(ctx_or_interaction : CtxOrInteraction) -> bool:
    data = get_access_data(ctx_or_interaction)
    if data is None or data.command_node is None:
        return True

    member = resolve_member(ctx_or_interaction)
    if member is None:
        if isinstance(ctx_or_interaction, discord.Interaction):
            raise e.BadEnvironmentDMs
        raise e.BadEnvironmentDMs

    if not evaluate_access(data.command_node, member):
        if isinstance(ctx_or_interaction, discord.Interaction):
            raise e.AppBadPermissionsCommand
        raise e.BadPermissionsCommand

    if data.channel_rules:
        channel_id = (
            ctx_or_interaction.channel_id
            if isinstance(ctx_or_interaction, discord.Interaction)
            else (ctx_or_interaction.channel.id if ctx_or_interaction.channel else None)
        )
        if channel_id is not None:
            allowed : list[int] = []
            for rule in data.channel_rules:
                if evaluate_access(rule.node, member):
                    allowed.extend(rule.channels)
            if allowed and channel_id not in allowed:
                if isinstance(ctx_or_interaction, discord.Interaction):
                    raise e.AppBadPermissionsCommand
                raise e.BadPermissionsCommand

    return True

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @access_control
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def access_control(
    *,
    command          : AccessNode               | None = None,
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    def decorator(func : CommandCallback[P, T_co]) -> CommandCallback[P, T_co]:
        data = AccessData(
            command_node   = command,
            argument_nodes = dict(argument_nodes),
            channel_rules  = list(channel_rules or []),
        )
        cast("AccessControlled", func).__access_data__ = data

        func = commands.check(access_predicate)(func)
        return app_commands.check(access_predicate)(func)

    return decorator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @bot_owner_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def bot_owner_cmd(
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    return access_control(
        command       = UserNode(user_id = BOT_OWNER_ID),
        channel_rules = channel_rules,
        **argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @director_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def director_cmd(
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    return access_control(
        command       = RoleNode(role_id = DIRECTORS_ROLE_ID),
        channel_rules = channel_rules,
        **argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @administrator/senior_administrator_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def administrator_cmd(
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    return access_control(
        command       = RoleNode(role_id = ADMINISTRATORS_ROLE_ID),
        channel_rules = channel_rules,
        **argument_nodes,
    )

def senior_administrator_cmd(
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    return access_control(
        command       = RoleNode(role_id = SENIOR_ADMINISTRATORS_ROLE_ID),
        channel_rules = channel_rules,
        **argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @moderator/senior_moderator_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def moderator_cmd(
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    return access_control(
        command       = RoleNode(role_id = MODERATORS_ROLE_ID),
        channel_rules = channel_rules,
        **argument_nodes,
    )

def senior_moderator_cmd(
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    return access_control(
        command       = RoleNode(role_id = SENIOR_MODERATORS_ROLE_ID),
        channel_rules = channel_rules,
        **argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @staff_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def staff_cmd(
    channel_rules    : list[ChannelRestriction] | None = None,
    **argument_nodes : AccessNode,
) -> Callable[[CommandCallback[P, T_co]], CommandCallback[P, T_co]]:
    return access_control(
        command = RoleNode(role_id = STAFF_ROLE_ID),
        channel_rules = channel_rules,
        **argument_nodes,
    )
