from collections.abc import Callable, Coroutine
from typing import Protocol, cast, ParamSpec, TypeVar

import discord
from discord import app_commands
from discord.ext import commands

from bot import Context, CtxOrInteraction, Interaction
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
    RoleNode,
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

P = ParamSpec("P")
T = TypeVar("T")

type CommandCallback[**P, T] = Callable[P, Coroutine[None, None, T]]
type Decorator[**P, T] = Callable[[CommandCallback[P, T]], CommandCallback[P, T]]
type ChannelRules = list[ChannelRestriction] | None
type ArgumentNodes = dict[str, AccessNode] | None

async def execute_access_check(ctx_or_interaction : CtxOrInteraction) -> bool:
    data = get_access_data(ctx_or_interaction)
    if data is None or (data.command_node is None and not data.guild_only and not data.dm_only):
        return True

    in_guild = ctx_or_interaction.guild is not None

    if data.guild_only and not in_guild:
        await e.send_bad_environment_dms(ctx_or_interaction)
        return False

    if data.dm_only and in_guild:
        await e.send_bad_environment_guild(ctx_or_interaction)
        return False

    if data.command_node is None:
        return True

    member = resolve_member(ctx_or_interaction)
    if member is None:
        await e.send_bad_environment_dms(ctx_or_interaction)
        return False

    if not evaluate_access(data.command_node, member):
        await e.send_bad_permissions_command(ctx_or_interaction)
        return False

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
                await e.send_bad_permissions_command(ctx_or_interaction)
                return False

    return True

async def prefix_access_predicate(ctx : Context) -> bool:
    return await execute_access_check(ctx)

async def app_access_predicate(interaction : Interaction) -> bool:
    return await execute_access_check(interaction)

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @access_control
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def access_control(
    *,
    command        : AccessNode | None = None,
    channel_rules  : ChannelRules      = None,
    guild_only     : bool              = False,
    dm_only        : bool              = False,
    argument_nodes : ArgumentNodes     = None,
) -> Decorator[P, T]:
    def decorator(func : CommandCallback[P, T]) -> CommandCallback[P, T]:
        data = AccessData(
            command_node   = command,
            argument_nodes = dict(argument_nodes or {}),
            channel_rules  = list(channel_rules or []),
            guild_only     = guild_only,
            dm_only        = dm_only,
        )
        cast("AccessControlled", func).__access_data__ = data

        func = commands.check(prefix_access_predicate)(func)
        return app_commands.check(app_access_predicate)(func)

    return decorator

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @bot_owner_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def bot_owner_cmd(
    channel_rules  : ChannelRules  = None,
    guild_only     : bool          = False,
    dm_only        : bool          = False,
    argument_nodes : ArgumentNodes = None,
) -> Decorator[P, T]:
    return access_control(
        command        = UserNode(user_id = BOT_OWNER_ID),
        channel_rules  = channel_rules,
        guild_only     = guild_only,
        dm_only        = dm_only,
        argument_nodes = argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @director_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def director_cmd(
    channel_rules  : ChannelRules  = None,
    argument_nodes : ArgumentNodes = None,
) -> Decorator[P, T]:
    return access_control(
        command        = RoleNode(role_id = DIRECTORS_ROLE_ID),
        channel_rules  = channel_rules,
        guild_only     = True,
        argument_nodes = argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @administrator/senior_administrator_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def administrator_cmd(
    channel_rules  : ChannelRules  = None,
    argument_nodes : ArgumentNodes = None,
) -> Decorator[P, T]:
    return access_control(
        command        = RoleNode(role_id = ADMINISTRATORS_ROLE_ID),
        channel_rules  = channel_rules,
        guild_only     = True,
        argument_nodes = argument_nodes,
    )

def senior_administrator_cmd(
    channel_rules  : ChannelRules  = None,
    argument_nodes : ArgumentNodes = None,
) -> Decorator[P, T]:
    return access_control(
        command        = RoleNode(role_id = SENIOR_ADMINISTRATORS_ROLE_ID),
        channel_rules  = channel_rules,
        guild_only     = True,
        argument_nodes = argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @moderator/senior_moderator_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def moderator_cmd(
    channel_rules  : ChannelRules  = None,
    argument_nodes : ArgumentNodes = None,
) -> Decorator[P, T]:
    return access_control(
        command        = RoleNode(role_id = MODERATORS_ROLE_ID),
        channel_rules  = channel_rules,
        guild_only     = True,
        argument_nodes = argument_nodes,
    )

def senior_moderator_cmd(
    channel_rules  : ChannelRules  = None,
    argument_nodes : ArgumentNodes = None,
) -> Decorator[P, T]:
    return access_control(
        command        = RoleNode(role_id = SENIOR_MODERATORS_ROLE_ID),
        channel_rules  = channel_rules,
        guild_only     = True,
        argument_nodes = argument_nodes,
    )

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# @staff_cmd
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

def staff_cmd(
    channel_rules  : ChannelRules  = None,
    argument_nodes : ArgumentNodes = None,
) -> Decorator[P, T]:
    return access_control(
        command        = RoleNode(role_id = STAFF_ROLE_ID),
        channel_rules  = channel_rules,
        guild_only     = True,
        argument_nodes = argument_nodes,
    )