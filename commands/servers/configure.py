from typing import Literal, final, override

from discord import ChannelType, Guild, Object

from bot import Interaction
from bot.ui import ActionRow, ChannelSelect, TextDisplay
from constants import ACCEPTED_EMOJI, DENIED_EMOJI
from core.exceptions import send_bad_operation
from core.paginator import NamedPaginator, PageData

type Keys = Literal["edit", "delete"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server configure Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def _get_channel_config(interaction : Interaction, key : Keys) -> int | None:
    key_dict : dict[Keys, str] = {
        "edit"   : "messages_edit_channel",
        "delete" : "messages_delete_channel",
    }

    fetched_key = key_dict[key]

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not interaction.guild:
        return None

    cursor = await interaction.client.db.execute(
        "SELECT config_value FROM GuildConfig WHERE guild_id = ? AND config_key = ?",
        (interaction.guild.id, fetched_key),
    )
    row = await cursor.fetchone()
    await cursor.close()

    return row[0] if row else None

async def _set_channel_config(interaction : Interaction, key : Keys, value : int) -> None:
    key_dict : dict[Keys, str] = {
        "edit"   : "messages_edit_channel",
        "delete" : "messages_delete_channel",
    }

    fetched_key = key_dict[key]

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not interaction.guild:
        return

    db = interaction.client.db

    await db.execute(
        (
            "INSERT INTO GuildConfig (guild_id, config_key, config_value) VALUES (?, ?, ?) "
            "ON CONFLICT (guild_id, config_key) DO UPDATE SET config_value = excluded.config_value"
        ),
        (interaction.guild.id, fetched_key, value),
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
        channel  = self.values[0]
        previous = self.default_values

        self.default_values = [Object(id = channel.id)]

        if not self.view:
            return

        try:
            await _set_channel_config(interaction, "edit", channel.id)
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
        channel  = self.values[0]
        previous = self.default_values

        self.default_values = [Object(id = channel.id)]

        if not self.view:
            return

        try:
            await _set_channel_config(interaction, "delete", channel.id)
            self.view.delete_id = channel.id
            self.view.update_pages()
            await interaction.response.edit_message(view = self.view)
        except Exception:
            self.default_values = previous
            await send_bad_operation(interaction, title = "update messages delete channel")
            raise

@final
class _ConfigurationView(NamedPaginator):
    def __init__(
        self,
        guild          : Guild,
        *,
        edit_channel   : int | None,
        delete_channel : int | None,
    ) -> None:
        self.guild     = guild
        self.edit_id   = edit_channel
        self.delete_id = delete_channel

        self.edit_select   = _MessagesEditSelect()
        self.delete_select = _MessagesDeleteSelect()

        if self.edit_id:
            self.edit_select.default_values = [Object(id = self.edit_id)]
        if self.delete_id:
            self.delete_select.default_values = [Object(id = self.delete_id)]

        initial_pages = [
            PageData(name = "Messages",   content = []),
            PageData(name = "Moderation", content = []),
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
                content = ["# Moderation", "This page doesn't display anything right now. :["],
            ),
        ]

        self.render()

async def run_server_configure(interaction : Interaction) -> None:

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if not interaction.guild:
        return

    edit_channel   = await _get_channel_config(interaction, "edit")
    delete_channel = await _get_channel_config(interaction, "delete")

    await interaction.response.send_message(
        view      = _ConfigurationView(
            interaction.guild,
            edit_channel   = edit_channel,
            delete_channel = delete_channel,
        ),
        ephemeral = True,
    )
