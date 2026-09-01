
from bot import Interaction
from core.exceptions import send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner style reset Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_style_reset(
    interaction : Interaction,
    *,
    branded     : bool | None = True,
) -> None:
    if branded is None:
        branded = True

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    try:
        await interaction.client.reset_name_style(interaction.guild, branded = branded)
        await format_send(
            interaction,
            msg_type = "success",
            title    = "reset display name style",
            subtitle = "The bot's display name style has been reset for this server",
        )
    except Exception as e:
        await send_bad_operation(
            interaction,
            title    = "reset display name style",
            subtitle = codeblock(f"{e}"),
        )
