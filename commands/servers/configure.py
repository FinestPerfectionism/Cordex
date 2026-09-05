from typing import Literal, Self, final, override

from discord import ChannelType, Guild, Object, TextChannel

from bot import Interaction
from bot.ui import (
    ActionRow,
    Button,
    ButtonSection,
    ChannelSelect,
    Checkbox,
    Label,
    Modal,
    RoleSelect,
    TextDisplay,
)
from constants import ACCEPTED_EMOJI, CONTESTED_EMOJI, DENIED_EMOJI
from core.exceptions import send_bad_argument, send_bad_operation
from core.moderation import Actions
from core.paginator import NamedPaginator, PageData

type Keys = Literal["edit", "delete", "quarantine", "enforce_channels", "enforce_roles"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server configure Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def _get_guild_config(interaction : Interaction, key : Keys) -> int | None:
    key_dict : dict[Keys, str] = {
        "edit"             : "messages_edit_channel",
        "delete"           : "messages_delete_channel",
        "quarantine"       : "quarantine_role",
        "enforce_channels" : "quarantine_enforce_channels",
        "enforce_roles"    : "quarantine_enforce_roles",
    }

    fetched_key = key_dict[key]

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not interaction.guild:
        return None

    cursor = await interaction.client.db.execute(
        t"SELECT config_value FROM GuildConfig WHERE guild_id = {interaction.guild.id} AND config_key = {fetched_key}",
    )

    row = await cursor.fetchone()
    await cursor.close()

    return row[0] if row else None

async def _set_guild_config(interaction : Interaction, key : Keys, value : int) -> None:
    key_dict : dict[Keys, str] = {
        "edit"             : "messages_edit_channel",
        "delete"           : "messages_delete_channel",
        "quarantine"       : "quarantine_role",
        "enforce_channels" : "quarantine_enforce_channels",
        "enforce_roles"    : "quarantine_enforce_roles",
    }

    fetched_key = key_dict[key]

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not interaction.guild:
        return

    db = interaction.client.db

    await db.execute(
        (
            t"INSERT INTO GuildConfig (guild_id, config_key, config_value) VALUES ({interaction.guild.id}, {fetched_key}, {value}) "
            t"ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value"
        ),
    )
    await db.commit()

@final
class _MessagesEditSelect(ChannelSelect["_ConfigurationView"]):
    def __init__(self) -> None:
        super().__init__(
            placeholder   = "Select a channel...",
            channel_types = [ChannelType.text],
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        guild = interaction.guild

        if not guild:
            return

        channel = guild.get_channel(self.values[0].id)

        if not isinstance(channel, TextChannel):
            return

        me = guild.me

        if not me:
            return

        permissions = channel.permissions_for(me)

        if not permissions.send_messages:
            await send_bad_argument(
                interaction,
                title    = "set edit channel",
                subtitle = {None : "I don't have permissions to send messages in that channel."},
            )
            return
        if not permissions.view_channel:
            await send_bad_argument(
                interaction,
                title    = "set edit channel",
                subtitle = {None : "I don't have permissions to view that channel."},
            )
            return

        if not self.view:
            return

        previous = self.default_values
        self.default_values = [Object(id = channel.id)]

        try:
            await _set_guild_config(interaction, "edit", channel.id)
            self.view.edit_id = channel.id
            self.view.update_pages()
            await interaction.response.edit_message(view = self.view)
        except Exception:
            self.default_values = previous
            await send_bad_operation(interaction, title = "update messages edit channel")
            raise

@final
class _MessagesDeleteSelect(ChannelSelect["_ConfigurationView"]):
    def __init__(self) -> None:
        super().__init__(
            placeholder   = "Select a channel...",
            channel_types = [ChannelType.text],
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        guild = interaction.guild

        if not guild:
            return

        channel = guild.get_channel(self.values[0].id)

        if not isinstance(channel, TextChannel):
            return

        me = guild.me

        if not me:
            return

        permissions = channel.permissions_for(me)

        if not permissions.send_messages:
            await send_bad_argument(
                interaction,
                title    = "set delete channel",
                subtitle = {None : "I don't have permissions to send messages in that channel."},
            )
            return
        if not permissions.view_channel:
            await send_bad_argument(
                interaction,
                title    = "set delete channel",
                subtitle = {None : "I don't have permissions to view that channel."},
            )
            return

        if not self.view:
            return

        previous = self.default_values
        self.default_values = [Object(id = channel.id)]

        try:
            await _set_guild_config(interaction, "delete", channel.id)
            self.view.delete_id = channel.id
            self.view.update_pages()
            await interaction.response.edit_message(view = self.view)
        except Exception:
            self.default_values = previous
            await send_bad_operation(interaction, title = "update messages delete channel")
            raise

@final
class _QuarantineRoleSelect(RoleSelect["_ConfigurationView"]):
    def __init__(self) -> None:
        super().__init__(placeholder = "Select a role...")

    @override
    async def callback(self, interaction : Interaction) -> None:
        role     = self.values[0]
        previous = self.default_values

        self.default_values = [Object(id = role.id)]

        if not interaction.guild:
            return

        if role >= interaction.guild.me.top_role:
            await send_bad_argument(
                interaction,
                title    = "set quarantine role",
                subtitle = {None : "That role is above or equal to my highest role, so I can't assign it."},
            )

        if not self.view:
            return

        actions = Actions(interaction.client, interaction.guild)

        try:
            await _set_guild_config(interaction, "quarantine", role.id)
            await actions.quarantine_enforce("Channel")
            await actions.quarantine_enforce("Role")
        except Exception:
            self.default_values = previous
            await send_bad_operation(interaction, title = "update quarantine role")
            raise

        self.view.quarantine_id = role.id
        self.view.update_pages()

        await interaction.response.edit_message(view = self.view)

@final
class _QuarantineEnforceModal(Modal, title = "Quarantine Enforce"):
    def __init__(self, view : _ConfigurationView) -> None:
        super().__init__()
        self.view = view

        missing : list[str] = []

        if not view.guild.me or not view.guild.me.guild_permissions.manage_channels:
            missing.append("`Manage Channels`")
        if not view.guild.me or not view.guild.me.guild_permissions.manage_roles:
            missing.append("`Manage Roles`")

        self.warning = TextDisplay[Self](
            (
               f"**{CONTESTED_EMOJI} Warning,**\n"
                "I lack the following permissions:\n"
               f"{"\n".join(f"- {permission}" for permission in missing)}\n"
                "Settings will have no effect and nothing will be enforced!"
            ),
        )

        self._channels = Checkbox[Self](default = view.enforce_channels)
        self.channels  = Label[Self](
            text        = "Channels",
            description = "Whether to automatically enforce permissions for the quarantine role on channels.",
            component   = self._channels,
        )

        self._roles = Checkbox[Self](default = view.enforce_roles)
        self.roles  = Label[Self](
            text        = "Roles",
            description = "Whether to automatically enforce permissions for the quarantine role on roles.",
            component   = self._roles,
        )

        if missing:
            self.add_item(self.warning)

        self.add_items(self.channels, self.roles)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        if not interaction.guild:
            return

        try:
            await _set_guild_config(interaction, "enforce_channels", int(self._channels.value))
            await _set_guild_config(interaction, "enforce_roles", int(self._roles.value))
        except Exception:
            await send_bad_operation(interaction, title = "update quarantine enforcement")
            raise

        channels = self._channels.value
        roles    = self._roles.value

        self.view.enforce_channels = channels
        self.view.enforce_roles    = roles
        self.view.update_pages()

        actions = Actions(interaction.client, interaction.guild)

        if channels:
            await actions.quarantine_enforce("Channel")
        if roles:
            await actions.quarantine_enforce("Role")

        await interaction.response.edit_message(view = self.view)

@final
class _QuarantineEnforceButton(Button["_ConfigurationView"]):
    def __init__(self) -> None:
        super().__init__(label = "Configure Enforcement")

    @override
    async def callback(self, interaction : Interaction) -> None:
        if not self.view:
            return

        await interaction.response.send_modal(_QuarantineEnforceModal(self.view))

@final
class _ConfigurationView(NamedPaginator):
    def __init__(
        self,
        guild            : Guild,
        *,
        edit_channel     : int | None,
        delete_channel   : int | None,
        quarantine_role  : int | None,
        enforce_channels : bool,
        enforce_roles    : bool,
    ) -> None:
        self.guild            = guild
        self.edit_id          = edit_channel
        self.delete_id        = delete_channel
        self.quarantine_id    = quarantine_role
        self.enforce_channels = enforce_channels
        self.enforce_roles    = enforce_roles

        self.edit_select            = _MessagesEditSelect()
        self.delete_select          = _MessagesDeleteSelect()
        self.quarantine_select      = _QuarantineRoleSelect()
        self.quarantine_enforce_btn = _QuarantineEnforceButton()

        if self.edit_id:
            self.edit_select.default_values = [Object(id = self.edit_id)]
        if self.delete_id:
            self.delete_select.default_values = [Object(id = self.delete_id)]
        if self.quarantine_id:
            self.quarantine_select.default_values = [Object(id = self.quarantine_id)]

        initial_pages = [
            PageData(name = "Messages",      content = []),
            PageData(name = "Moderation",    content = []),
            PageData(name = "Configurators", content = []),
        ]

        super().__init__(initial_pages, container = True)
        self.update_pages()

    def update_pages(self) -> None:
        edit = self.guild.get_channel(self.edit_id) if self.edit_id else None
        if edit:
            txt_edit = (
                f"{ACCEPTED_EMOJI} **Messages Edit Channel Set**\n"
                f"Message edits will be sent to {edit.mention}."
            )
        else:
            txt_edit = (
                f"{DENIED_EMOJI} **Messages Edit Channel Unset**\n"
                "Set one with the select below."
            )

        delete = self.guild.get_channel(self.delete_id) if self.delete_id else None
        if delete:
            txt_delete = (
                f"{ACCEPTED_EMOJI} **Messages Delete Channel Set**\n"
                f"Message deletions will be sent to {delete.mention}."
            )
        else:
            txt_delete = (
                f"{DENIED_EMOJI} **Messages Delete Channel Unset**\n"
                "Set one with the select below."
            )

        quarantine = self.guild.get_role(self.quarantine_id) if self.quarantine_id else None
        if quarantine:
            issues : list[str] = []
            me = self.guild.me

            if me:
                if self.enforce_channels and not me.guild_permissions.manage_channels:
                    issues.append("I lack the `Manage Channels` permission to enforce channel permissions.")

                if self.enforce_roles and not me.guild_permissions.manage_roles:
                    issues.append("I lack the `Manage Roles` permission to enforce role permissions.")

                if not me.guild_permissions.manage_roles:
                    issues.append("I lack the `Manage Roles` permission to assign the quarantine role to members.")

                roles_by_pos = sorted(self.guild.roles, key = lambda r : r.position, reverse = True)
                top_role = roles_by_pos[0] if roles_by_pos else None

                if me.top_role != top_role:
                    issues.append("My highest role is not at the absolute top of the role hierarchy.")

                if me.top_role.position - quarantine.position != 1:
                    issues.append("The quarantine role is not directly below my highest role.")

            if issues:
                formatted_issues = "\n".join(f"- {issue}" for issue in issues)
                txt_quarantine = (
                    f"{CONTESTED_EMOJI} **Quarantine Role Misconfigured**\n"
                    f"Quarantined members will receive the {quarantine.mention} role, but issues were detected:\n"
                    f"{formatted_issues}"
                )
            else:
                txt_quarantine = (
                    f"{ACCEPTED_EMOJI} **Quarantine Role Set**\n"
                    f"Quarantined members will receive the {quarantine.mention} role."
                )
        else:
            txt_quarantine = (
                f"{DENIED_EMOJI} **Quarantine Role Unset**\n"
                f"Set one with the select below."
            )

        self.pages = [
            PageData(
                name    = "Messages",
                content = [
                    "# Messages",
                    TextDisplay(txt_edit),
                    ActionRow(self.edit_select),
                    TextDisplay(txt_delete),
                    ActionRow(self.delete_select),
                ],
            ),
            PageData(
                name    = "Moderation",
                content = [
                    "# Moderation",
                    ButtonSection(txt_quarantine, button = self.quarantine_enforce_btn),
                    ActionRow(self.quarantine_select),
                ],
            ),
            PageData(
                name    = "Configurators",
                content = ["# Configurators", "This page doesn't display anything right now. :["],
            ),
        ]

        self.render()

async def run_server_configure(interaction : Interaction) -> None:

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not interaction.guild:
        return

    edit_channel     = await _get_guild_config(interaction, "edit")
    delete_channel   = await _get_guild_config(interaction, "delete")
    quarantine_role  = await _get_guild_config(interaction, "quarantine")
    enforce_channels = await _get_guild_config(interaction, "enforce_channels")
    enforce_roles    = await _get_guild_config(interaction, "enforce_roles")

    await interaction.response.send_message(
        view      = _ConfigurationView(
            interaction.guild,
            edit_channel     = edit_channel,
            delete_channel   = delete_channel,
            quarantine_role  = quarantine_role,
            enforce_channels = bool(enforce_channels),
            enforce_roles    = bool(enforce_roles),
        ),
        ephemeral = True,
    )
