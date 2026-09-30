from dataclasses import dataclass

from discord import Member

from bot.types import GuildMessagable

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Moderation Action Payloads
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@dataclass
class _BaseRemovePayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class _BaseAddPayload:
    moderator : Member
    target    : Member
    reason    : str
    dm_user   : bool


@dataclass
class _BaseLockdownPayload:
    moderator : Member
    target    : GuildMessagable
    reason    : str


@dataclass
class LockdownAddPayload(_BaseLockdownPayload):
    """
    Represents a lockdown add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the lockdown add.
    target : `GuildMessagable`
        The target channel of the lockdown add.
    reason : `str`
        The reason for the lockdown add.
    """


@dataclass
class LockdownRemovePayload(_BaseLockdownPayload):
    """
    Represents a lockdown remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the lockdown remove.
    target : `GuildMessagable`
        The target channel of the lockdown remove.
    reason : `str`
        The reason for the lockdown remove.
    """


@dataclass
class BanAddPayload(_BaseAddPayload):
    """
    Represents a ban add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the ban add.
    target : `Member`
        The target member of the ban add.
    reason : `str`
        The reason for the ban add.
    dm_user : `bool`
        Whether the user was direct messaged.
    seconds_to_delete : `int`
        The duration in seconds of messages to delete.
    """

    seconds_to_delete : int


@dataclass
class BanRemovePayload(_BaseRemovePayload):
    """
    Represents a ban remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the ban remove.
    target : `Member`
        The target member of the ban remove.
    reason : `str`
        The reason for the ban remove.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class KickPayload(_BaseAddPayload):
    """
    Represents a kick action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the kick.
    target : `Member`
        The target member of the kick.
    reason : `str`
        The reason for the kick.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class TimeoutAddPayload(_BaseAddPayload):
    """
    Represents a timeout add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the timeout add.
    target : `Member`
        The target member of the timeout add.
    reason : `str`
        The reason for the timeout add.
    dm_user : `bool`
        Whether the user was direct messaged.
    length : `int`
        The duration of the timeout in seconds.
    """

    length : int


@dataclass
class TimeoutRemovePayload(_BaseRemovePayload):
    """
    Represents a timeout remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the timeout remove.
    target : `Member`
        The target member of the timeout remove.
    reason : `str`
        The reason for the timeout remove.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class QuarantineAddPayload(_BaseAddPayload):
    """
    Represents a quarantine add action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the quarantine add.
    target : `Member`
        The target member of the quarantine add.
    reason : `str`
        The reason for the quarantine add.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class QuarantineRemovePayload(_BaseRemovePayload):
    """
    Represents a quarantine remove action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the quarantine remove.
    target : `Member`
        The target member of the quarantine remove.
    reason : `str`
        The reason for the quarantine remove.
    dm_user : `bool`
        Whether the user was direct messaged.
    """


@dataclass
class PurgePayload:
    """
    Represents a purge action.

    Parameters
    ----------
    moderator : `Member`
        The moderator responsible for the purge.
    target : `Member | None`
        The optional target member whose messages were purged.
    reason : `str`
        The reason for the purge.
    channel : `GuildMessagable`
        The target channel of the purge.
    amount : `int`
        The amount of messages purged.
    force : `bool`
        Whether the purge was forced.
    """

    moderator : Member
    target    : Member | None
    reason    : str
    channel   : GuildMessagable
    amount    : int
    force     : bool


Payloads = (
    LockdownAddPayload
    | LockdownRemovePayload
    | BanAddPayload
    | BanRemovePayload
    | KickPayload
    | QuarantineAddPayload
    | QuarantineRemovePayload
    | TimeoutAddPayload
    | TimeoutRemovePayload
    | PurgePayload
)
