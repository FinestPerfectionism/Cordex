import re
import uuid
from pathlib import Path

import discord
from discord import Attachment, TextChannel, User
from discord.app_commands import (
    Choice,
    autocomplete,
    command,
    describe,
    guild_only,
    rename,
)
from discord.ext import commands

from bot import Cordex, Interaction, log
from constants import PARTNERSHIPS_CHANNEL_ID
from core.exceptions import send_bad_argument, send_bad_operation
from core.permissions import director_cmd
from core.responses import format_send
from core.state import (
    IMAGE_DIR,
    PartnershipEntry,
    load_partnership_data,
    save_partnership_data,
)
from guild_info.partnerships import rebuild_partnership_view

INVITE_RE = re.compile(r"^(https?://)?(www\.)?(discord\.gg|discord\.com/invite)/[A-Za-z0-9-]+$")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Partnership Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@guild_only
class PartnershipCommands(commands.GroupCog):
    def __init__(self, bot : Cordex) -> None:
        self.bot : Cordex = bot

    async def get_channel(self, interaction : Interaction) -> TextChannel | None:
        channel = self.bot.get_channel(PARTNERSHIPS_CHANNEL_ID)
        if not isinstance(channel, TextChannel):
            await format_send(
                interaction,
                msg_type          = "error",
                title             = "update",
                subtitle          = "The partnerships channel ID is missing or points to the wrong channel type.",
                footer            = "Bad configuration",
            )
            return None
        return channel

    async def server_name_autocomplete(self, _interaction : Interaction, current : str) -> list[Choice[str]]:
        data = await load_partnership_data(self.bot.db)
        return [
            Choice(name = p["server_name"], value = p["server_name"])
            for p in data["partnerships"] if current.lower() in p["server_name"].lower()
        ][:25]

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /partnership add
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(name = "add", description = "Add a server partnership.")
    @describe(
        server_picture     = "The server's picture.",
        server_name        = "The server's name.",
        server_description = "The server's description.",
        server_owner       = "The server's owner.",
        server_link        = "The server's invite link. Must be a valid Discord invite of the form `https://discord.gg/example`.",
    )
    @director_cmd()
    @rename(
        server_picture     = "server-picture",
        server_name        = "server-name",
        server_description = "server-description",
        server_owner       = "server-owner",
        server_link        = "server-link",
    )
    async def cmd_partnership_add(
        self,
        interaction        : Interaction,
        server_picture     : Attachment,
        server_name        : str,
        server_description : str,
        server_owner       : User,
        server_link        : str,
    ) -> None:
        if not INVITE_RE.match(server_link):
            await send_bad_argument(interaction, subtitle = {"server-link" : "The server link must be a valid Discord invite."})
            return

        await interaction.response.defer(ephemeral = True)

        channel = await self.get_channel(interaction)
        if channel is None:
            return

        IMAGE_DIR.mkdir(parents = True, exist_ok = True)

        suffix     = Path(server_picture.filename).suffix or ".png"
        filename   = f"{uuid.uuid4()}{suffix}"
        image_path = IMAGE_DIR / filename

        try:
            image_bytes = await server_picture.read()
            image_path.write_bytes(image_bytes)

        except discord.HTTPException:
            log.exception("Failed to download partnership attachment")
            await send_bad_operation(interaction, title = "download the server picture")
            raise

        except OSError:
            log.exception("Failed to save partnership attachment to disk")
            await send_bad_operation(interaction, title = "save the server picture")
            raise

        data        = await load_partnership_data(self.bot.db)
        description = server_description.replace("\\n", "\n")

        entry : PartnershipEntry = {
            "server_name"        : server_name,
            "server_description" : description,
            "server_owner_id"    : server_owner.id,
            "server_link"        : server_link,
            "image_filename"     : filename,
        }
        data["partnerships"].append(entry)

        await format_send(
            interaction,
            msg_type =  "success",
            title    = f"added partnership with {server_name}",
            subtitle =  "Updating the channel...",
        )

        try:
            await rebuild_partnership_view(self.bot, data["partnerships"])
        except discord.HTTPException:
            log.exception("Failed to rebuild partnership layout after add")
            data["partnerships"].pop()
            image_path.unlink(missing_ok = True)
            await send_bad_operation(
                interaction,
                title    =  "update the partnerships channel",
                subtitle = f"**{server_name}** was added to the data but the channel failed to rebuild. The entry has been rolled back.",
            )
            raise

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /partnership remove
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(name = "remove", description = "Remove a server partnership.")
    @describe(server_name = "The name of the server to remove.")
    @director_cmd()
    async def cmd_partnership_remove(self, interaction : Interaction, server_name : str) -> None:
        await interaction.response.defer(ephemeral = True)

        channel = await self.get_channel(interaction)
        if channel is None:
            return

        data    = await load_partnership_data(self.bot.db)
        matches = [p for p in data["partnerships"] if p["server_name"] == server_name]

        if not matches:
            await format_send(
                interaction,
                msg_type =  "warning",
                title    = f'find partnership "{server_name}"',
                subtitle =  "No partnership exists with that name. Check the spelling or use the autocomplete.",
                footer   =  "Bad argument",
            )
            return

        removed  = matches[0]
        original = list(data["partnerships"])
        data["partnerships"] = [p for p in data["partnerships"] if p["server_name"] != server_name]

        await format_send(
            interaction,
            msg_type =  "success",
            title    = f"removed partnership with {server_name}",
            subtitle =  "Updating the channel...",
        )

        try:
            await rebuild_partnership_view(self.bot, data["partnerships"])

        except discord.HTTPException:
            log.exception("Failed to rebuild partnership layout after remove")
            data["partnerships"] = original
            await save_partnership_data(self.bot.db, data)
            await format_send(
                interaction,
                msg_type =  "error",
                title    =  "update the partnerships channel",
                subtitle = f"**{server_name}** was removed from the data but the channel failed to rebuild. The entry has been restored.",
                footer   =  "Bad operation",
            )
            return

        (IMAGE_DIR / removed["image_filename"]).unlink(missing_ok = True)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /partnership update
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @command(name = "update", description = "Update an existing server partnership.")
    @describe(
        server_name        = "The name of the server to update.",
        server_picture     = "The server's new picture.",
        new_server_name    = "The server's new name.",
        server_description = "The server's new description.",
        server_owner       = "The server's new owner.",
        server_link        = "The server's new invite link. Must be a valid Discord invite of the form `https://discord.gg/example`.",
    )
    @autocomplete(server_name = server_name_autocomplete)
    @director_cmd()
    async def cmd_partnership_update(
        self,
        interaction        : Interaction,
        server_name        : str,
        server_picture     : Attachment | None = None,
        new_server_name    : str        | None = None,
        server_description : str        | None = None,
        server_owner       : User       | None = None,
        server_link        : str        | None = None,
    ) -> None:
        if server_link is not None and not INVITE_RE.match(server_link):
            await format_send(
                interaction,
                msg_type = "warning",
                title    = "update partnership",
                subtitle = "The new server link must be a valid Discord invite.",
                footer   = "Bad argument",
            )
            return

        await interaction.response.defer(ephemeral = True)

        if (await self.get_channel(interaction)) is None:
            return

        data    = await load_partnership_data(self.bot.db)
        matches = [p for p in data["partnerships"] if p["server_name"] == server_name]

        if not matches:
            await format_send(
                interaction,
                msg_type =  "warning",
                title    = f'find partnership "{server_name}"',
                subtitle =  "No partnership exists with that name. Check the spelling or use the autocomplete.",
                footer   =  "Bad argument",
            )
            return

        entry               = matches[0]
        old_image_filename  : str | None = None

        if server_picture is not None:
            IMAGE_DIR.mkdir(parents = True, exist_ok = True)
            suffix         = Path(server_picture.filename).suffix or ".png"
            new_filename   = f"{uuid.uuid4()}{suffix}"
            new_image_path = IMAGE_DIR / new_filename

            try:
                image_bytes = await server_picture.read()
                new_image_path.write_bytes(image_bytes)
                old_image_filename      = entry["image_filename"]
                entry["image_filename"] = new_filename

            except discord.HTTPException:
                log.exception("Failed to download updated partnership attachment")
                await format_send(
                    interaction,
                    msg_type = "error",
                    title    = "download the new server picture",
                    subtitle = "Discord returned an error while fetching the attachment. No changes were saved.",
                    footer   = "Bad operation",
                )
                return

            except OSError:
                log.exception("Failed to save updated partnership image to disk")
                await format_send(
                    interaction,
                    msg_type = "error",
                    title    = "save the new server picture",
                    subtitle = "The image was downloaded but could not be written to disk. No changes were saved.",
                    footer   = "Bad operation",
                )
                return

        if new_server_name is not None:
            entry["server_name"] = new_server_name
        if server_description is not None:
            entry["server_description"] = server_description.replace("\\n", "\n")
        if server_owner is not None:
            entry["server_owner_id"] = server_owner.id
        if server_link is not None:
            entry["server_link"] = server_link

        display_name = entry["server_name"]

        await format_send(
            interaction,
            msg_type =  "success",
            title    = f"updated partnership with {server_name}",
            subtitle =  "Updating the channel...",
        )

        try:
            await rebuild_partnership_view(self.bot, data["partnerships"])

        except discord.HTTPException:
            log.exception("Failed to rebuild partnership layout after update")
            await format_send(
                interaction,
                msg_type          =  "error",
                title             =  "update the partnerships channel",
                subtitle          = f"**{display_name}** was edited in the data but the channel failed to rebuild.",
                footer            =  "Bad operation",
            )
            return

        if old_image_filename is not None:
            (IMAGE_DIR / old_image_filename).unlink(missing_ok = True)

async def setup(bot : Cordex):
    cog = PartnershipCommands(bot)
    await bot.add_cog(cog)
