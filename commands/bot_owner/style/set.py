from re import compile

from bot import Cordex, Interaction
from constants import DisplayNameEffect, DisplayNameFont
from core.exceptions import send_bad_argument, send_bad_operation
from core.responses import format_send
from core.utilities import codeblock

COLOR_PATTERN = compile(r"^[0-9a-fA-F]{6}(?:-[0-9a-fA-F]{6})?$")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner style set Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

async def run_bo_style_set(
    interaction : Interaction,
    bot         : Cordex,
    font        : str,
    effect      : str,
    colors      : str,
) -> None:

    # ⸻ We know that the command will run in a guild but the type checker doesn't...

    if interaction.guild is None:
        return

    is_valid = bool(COLOR_PATTERN.match(colors))
    has_dash = "-" in colors

    if not is_valid or (effect == "gradient" and not has_dash) or (effect != "gradient" and has_dash):
        error = (
            "Gradient must be of the form `ABCDEF-123456`."
            if effect == "gradient" else
            "Color must be of the form `ABCDEF`."
        )

        await send_bad_argument(
            interaction,
            title    = "set display name style",
            subtitle = {"colors" : error},
        )
        return

    color_list = colors.split("-")

    try:
        await bot.set_name_style(
            guild     = interaction.guild,
            font_id   = DisplayNameFont[font],
            effect_id = DisplayNameEffect[effect],
            colors    = color_list,
        )
        await format_send(
            interaction,
            msg_type = "success",
            title    = "set display name style",
            subtitle = "The bot's display name style has been set for this server.",
        )
    except Exception as e:
        await send_bad_operation(
            interaction,
            title    = "set display name style",
            subtitle = codeblock(f"{e}"),
        )
