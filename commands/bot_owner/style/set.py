from re import compile
from typing import Self, final, override

from discord import SelectOption

from bot import Interaction
from bot.types import NameStyleResult
from bot.ui import Label, Modal, Select, TextInput
from constants import DisplayNameEffect, DisplayNameFont
from core.exceptions import (
    send_bad_argument,
    send_bad_environment_guild,
    send_bad_operation,
)
from core.responses import format_send
from core.utilities import codeblock

COLOR_PATTERN = compile(r"^[0-9a-fA-F]{6}(?:-[0-9a-fA-F]{6})?$")

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /bot-owner style set Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻

@final
class _StyleModal(Modal, title = "Set Display Name Style"):
    def __init__(self, current_style : NameStyleResult) -> None:
        super().__init__()

        font_enum   = current_style.font_id
        effect_enum = current_style.effect_id
        colors_list = current_style.colors

        font_options   = [
            ("Sakura",            "cherry_bomb"),
            ("Jellybean",         "chicle"),
            ("Modern",            "museo_moderno"),
            ("Medieval",          "neo_castel"),
            ("8Bit",              "pixelify"),
            ("Vampyre",           "sinistre"),
            ("GG Sans [Default]", "default"),
            ("Tempo",             "zilla_slab"),
        ]
        effect_options = [
            ("Solid",    "solid"),
            ("Gradient", "gradient"),
            ("Neon",     "neon"),
            ("Toon",     "toon"),
            ("Pop",      "pop"),
        ]

        self._font   = Select[Self](
            placeholder = "Select a font...",
            required    = False,
            options     = [
                SelectOption(
                    label   = label,
                    value   = value,
                    default = (font_enum.name == value),
                ) for label, value in font_options
            ],
        )
        self.font    = Label(
            text        = "Font",
            description = "The display name's font.",
            component   = self._font,
        )

        self._effect = Select[Self](
            placeholder = "Select an effect...",
            required    = False,
            options     = [
                SelectOption(label = label, value = value, default = (effect_enum.name == value))
                for label, value in effect_options
            ],
        )
        self.effect  = Label(
            text        = "Effect",
            description = "The display name's effect.",
            component   = self._effect,
        )

        if effect_enum == DisplayNameEffect.gradient and len(colors_list) == 1:
            colors_default = f"{colors_list[0]}-{colors_list[0]}"
        else:
            colors_default = "-".join(colors_list)

        self._colors = TextInput[Self](
            placeholder = "ABCDEF or ABCDEF-123456",
            default     = colors_default,
            required    = False,
            min_length  = 6,
            max_length  = 13,
        )
        self.colors  = Label(
            text        = "Color(s)",
            description = "The display name's color(s).",
            component   = self._colors,
        )

        self.add_items(self.font, self.effect, self.colors)

    @override
    async def on_submit(self, interaction : Interaction) -> None:

        # ⸻ We know that the command will run in a guild but the type checker doesn't...

        if interaction.guild is None:
            return

        # ⸻ Grab the modal values.

        font_value   = self._font.values[0]       if self._font.values   else None
        effect_value = self._effect.values[0]     if self._effect.values else None
        colors_value = self._colors.value.strip() if self._colors.value  else None

        # ⸻ No argument passed.

        if font_value is None and effect_value is None and colors_value is None:
            await send_bad_argument(
                interaction,
                title    = "set display name style",
                subtitle = {("font", "effect", "colors") : "At least one argument must be chosen."},
            )
            return

        try:
            current_style = await interaction.client.get_name_style(interaction.guild)

            font_enum   = DisplayNameFont[font_value]     if font_value   is not None else current_style.font_id
            effect_enum = DisplayNameEffect[effect_value] if effect_value is not None else current_style.effect_id

            if colors_value is not None:
                is_valid = bool(COLOR_PATTERN.match(colors_value))
                has_dash = "-" in colors_value

                # ⸻ Incorrect format for Color/Gradient was passed.

                if not (
                    is_valid or (
                        effect_enum == DisplayNameEffect.gradient
                        and not has_dash
                    ) or (effect_enum != DisplayNameEffect.gradient and has_dash)
                ):
                    error = (
                        "Gradient must be of the form `ABCDEF-123456`."
                        if effect_enum == DisplayNameEffect.gradient else
                        "Color must be of the form `ABCDEF`."
                    )

                    await send_bad_argument(
                        interaction,
                        title    = "set display name style",
                        subtitle = {"colors" : error},
                    )
                    return

                color_list = colors_value.split("-")
            else:
                color_list = current_style.colors

            await interaction.client.set_name_style(
                guild     = interaction.guild,
                font_id   = font_enum,
                effect_id = effect_enum,
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

async def run_bo_style_set(interaction : Interaction) -> None:
    if not interaction.guild:
        await send_bad_environment_guild(interaction)
        return

    style = await interaction.client.get_name_style(interaction.guild)
    await interaction.response.send_modal(_StyleModal(style))
