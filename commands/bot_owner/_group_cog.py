from typing import final

from discord import Message
from discord.app_commands import (
    Choice,
    ContextMenu,
    Group,
    autocomplete,
    describe,
    rename,
)
from discord.ext import commands
from discord.ext.commands import (  # type: ignore[reportMissingTypeStubs]
    command as prefix_command,
)

from bot import Context, Cordex, Interaction, log
from core.permissions import bot_owner_cmd

from ._base import get_cogs
from .cogs import (
    run_bo_cog_load,
    run_bo_cog_pullreload,
    run_bo_cog_reload,
    run_bo_cog_unload,
)
from .eval import eval_message_ids, run_bo_eval
from .messages import (
    run_bo_messages_delete,
    run_bo_messages_delete_menu,
    run_bo_messages_edit,
    run_bo_messages_edit_menu,
    run_bo_messages_reply_menu,
    run_bo_messages_send,
)
from .state import run_bo_state_restart, run_bo_state_shutdown, run_bo_state_sync
from .style import run_bo_style_reset, run_bo_style_set

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# Bot Owner Group Commands
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class BotOwnerCommands(
    commands.GroupCog,
    name        = "bot-owner",
    description = "Bot Owner only —— Bot owner commands.",
):
    def __init__(self, bot : Cordex) -> None:
        super().__init__()
        self.bot  = bot
        self.tree = bot.tree

        self.tree.add_command(
            ContextMenu(
                name     = "Reply to Message",
                callback = self.menu_bo_messages_reply,
            ),
        )
        self.tree.add_command(
            ContextMenu(
                name     = "Edit Message",
                callback = self.menu_bo_messages_edit,
            ),
        )
        self.tree.add_command(
            ContextMenu(
                name     = "Delete Message",
                callback = self.menu_bo_messages_delete,
            ),
        )

    cog     : Group = Group(
        name        = "cog",
        description = "Bot owner cog commands.",
    )
    message : Group = Group(
        name        = "message",
        description = "Bot owner message commands.",
    )
    state   : Group = Group(
        name        = "state",
        description = "Bot owner state commands.",
    )
    style   : Group = Group(
        name        = "style",
        description = "Bot owner style commands.",
    )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command Edit Listener
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @commands.Cog.listener("on_message_edit")
    async def message_edit_handler(self, _before : Message, after : Message) -> None:
        target_id = int(after.id)

        # ⸻ Eval command editing.

        log.info(f"Pre-eval log block. Target ID: {target_id}, Map: {eval_message_ids}")
        if target_id in eval_message_ids:
            log.info("Entered primary eval block.")

            # ⸻ Remove our old reactions.

            if self.bot.user is not None:
                log.info("Entered 'self.bot.user is not None' block.")
                for reaction in after.reactions:
                    log.info("Entered 'for reaction in reactions' block.")
                    if reaction.me:
                        log.info("Entered 'if reaction.me' block.")
                        try:
                            await reaction.remove(self.bot.user)
                        except Exception:
                            log.exception("Failure in eval command reinvocation — 'reaction.remove(self.bot.user)'")

            # ⸻ Remove our old response.

            old_response_id = eval_message_ids.pop(target_id, None)
            if old_response_id is not None:
                log.info("Entered 'if old_response_id is not None' block.")

                try:
                    old_msg = await after.channel.fetch_message(int(old_response_id))
                    await old_msg.delete()
                except Exception:
                    log.exception("Failure in eval command reinvocation — 'old_msg.delete()'")

            # ⸻ Reinvoke the command.

            try:
                ctx = await self.bot.get_context(after)
                if ctx.command is None:
                    ctx.command = self.cmd_bo_eval
                await self.bot.invoke(ctx)
            except Exception:
                log.exception("Failure in eval command reinvocation — 'self.bot.invoke(ctx)'")

            return

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Cog Autocomplete
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def _cog_autocomplete(self, _interaction : Interaction, current : str) -> list[Choice[str]]:
        return [
            Choice(name = cog, value = cog)
            for cog in get_cogs() if current.lower() in cog.lower()
        ][:25]

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog pull-reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "pull-reload",
        description = "Pull from main, then reload all cogs.",
    )
    @bot_owner_cmd()
    async def cmd_bo_cog_pullreload(self, interaction : Interaction) -> None:
        await run_bo_cog_pullreload(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog reload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "reload",
        description = "Reload a cog or all cogs.",
    )
    @describe(cog = "The cog to reload. Leave empty to reload all cogs.")
    @autocomplete(cog = _cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_cog_reload(self, interaction : Interaction, cog : str | None) -> None:
        await run_bo_cog_reload(interaction, cog)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog load Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "load",
        description = "Load a cog.",
    )
    @describe(cog = "The cog to load.")
    @autocomplete(cog = _cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_cog_load(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cog_load(interaction, cog)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner cog unload Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @cog.command(
        name        = "unload",
        description = "Unload a cog.",
    )
    @describe(cog = "The cog to unload.")
    @autocomplete(cog = _cog_autocomplete)
    @bot_owner_cmd()
    async def cmd_bo_cog_unload(self, interaction : Interaction, cog : str) -> None:
        await run_bo_cog_unload(interaction, cog)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state shutdown Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "shutdown",
        description = "Shutdown the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_shutdown(self, interaction : Interaction) -> None:
        await run_bo_state_shutdown(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state restart Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "restart",
        description = "Restart the bot.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_restart(self, interaction : Interaction) -> None:
        await run_bo_state_restart(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner state sync Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @state.command(
        name        = "sync",
        description = "Sync the bot tree.",
    )
    @bot_owner_cmd()
    async def cmd_bo_state_sync(self, interaction : Interaction) -> None:
        await run_bo_state_sync(interaction)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # .eval Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @prefix_command(name = "eval")
    async def cmd_bo_eval(self, ctx : Context, *, body : str) -> None:
        await run_bo_eval(ctx, body)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner message send Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @message.command(
        name        = "send",
        description = "Make the bot send something.",
    )
    @describe(
        text     = "The text to send.",
        reply_id = "The ID of the message to reply to.",
        ping     = "Whether to mention the user upon replying. Does nothing if reply-id is None.",
    )
    @rename(reply_id = "reply-id")
    @bot_owner_cmd()
    async def cmd_bo_messages_send(
        self,
        interaction : Interaction,
        text        : str,
        reply_id    : str         | None = None,
        *,
        ping        : bool        | None = True,
    ) -> None:
        await run_bo_messages_send(
            interaction,
            text,
            reply_id,
            ping = ping,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Reply to Message — Message Menu
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def menu_bo_messages_reply(self, interaction : Interaction, message : Message) -> None:
        await run_bo_messages_reply_menu(interaction, message)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner message edit Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @message.command(
        name        = "edit",
        description = "Make the bot edit one of its own messages.",
    )
    @describe(
        text       = "The new text for the message.",
        message_id = "The ID of the message to edit.",
    )
    @rename(message_id = "message-id")
    @bot_owner_cmd()
    async def cmd_bo_messages_edit(
        self,
        interaction : Interaction,
        text        : str,
        message_id  : str,
    ) -> None:
        await run_bo_messages_edit(interaction, text, message_id)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Edit Message — Message Menu
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def menu_bo_messages_edit(self, interaction : Interaction, message : Message) -> None:
        await run_bo_messages_edit_menu(interaction, message)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner message delete Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @message.command(
        name        = "delete",
        description = "Make the bot delete one of its own messages.",
    )
    @describe(message_id = "The ID of the message to delete.")
    @rename(message_id = "message-id")
    @bot_owner_cmd()
    async def cmd_bo_messages_delete(
        self,
        interaction : Interaction,
        message_id  : str,
    ) -> None:
        await run_bo_messages_delete(interaction, message_id)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # Delete Message — Message Menu
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    async def menu_bo_messages_delete(self, interaction : Interaction, message : Message) -> None:
        await run_bo_messages_delete_menu(interaction, message)

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner style reset Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @style.command(
        name        = "reset",
        description = "Reset the bot's server specfiic display name style.",
    )
    @describe(branded = "Whether the reset should be the bot's branding instead of normal font. Defaults to True.")
    async def cmd_bo_style_reset(self, interaction : Interaction, *, branded : bool | None = None) -> None:
        await run_bo_style_reset(
            interaction = interaction,
            branded     = branded,
        )

    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
    # /bot-owner style set Command
    # ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

    @style.command(
        name        = "set",
        description = "Set the bot's server specfiic display name style.",
    )
    @bot_owner_cmd()
    async def cmd_bo_style_set(self, interaction : Interaction) -> None:
        await run_bo_style_set(interaction)

async def setup(bot : Cordex) -> None:
    cog = BotOwnerCommands(bot)
    await bot.add_cog(cog)
