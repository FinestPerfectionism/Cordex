# pyright: reportIncompatibleMethodOverride = false

import re
from typing import Literal, Self, final, override

from discord import HTTPException, SelectOption

from bot import Interaction
from bot.types import NameStyleResult
from bot.ui import (
    ActionRow,
    Button,
    ButtonSection,
    Checkbox,
    FileUpload,
    Label,
    Modal,
    Select,
    TextDisplay,
    TextInput,
)
from constants import (
    EIGHTBIT_FONT_EMOJI,
    GG_SANS_FONT_EMOJI,
    JELLYBEAN_FONT_EMOJI,
    MEDIEVAL_FONT_EMOJI,
    MODERN_FONT_EMOJI,
    SAKURA_FONT_EMOJI,
    TEMPO_FONT_EMOJI,
    VAMPYRE_FONT_EMOJI,
    DisplayNameEffect,
    DisplayNameFont,
)
from core.exceptions import send_bad_argument, send_bad_operation
from core.paginator import NamedPaginator, PageData
from core.utilities import codeblock

COLOR_PATTERN = re.compile(r"^[0-9a-fA-F]{6}(?:-[0-9a-fA-F]{6})?$")

FONT_OPTIONS = [
    ("GG Sans",   "Discord's GG Sans font.", "default",       GG_SANS_FONT_EMOJI),
    ("Tempo",     "Tempo font.",             "zilla_slab",    TEMPO_FONT_EMOJI),
    ("Sakura",    "Sakura font.",            "cherry_bomb",   SAKURA_FONT_EMOJI),
    ("Jellybean", "Jellybean font.",         "chicle",        JELLYBEAN_FONT_EMOJI),
    ("Modern",    "Modern font.",            "museo_moderno", MODERN_FONT_EMOJI),
    ("Medieval",  "Medieval font.",          "neo_castel",    MEDIEVAL_FONT_EMOJI),
    ("8Bit",      "8Bit font.",              "pixelify",      EIGHTBIT_FONT_EMOJI),
    ("Vampyre",   "Vampyre font.",           "sinistre",      VAMPYRE_FONT_EMOJI),
]

EFFECT_OPTIONS = [
    ("Solid",    "solid"),
    ("Gradient", "gradient"),
    ("Neon",     "neon"),
    ("Toon",     "toon"),
    ("Pop",      "pop"),
]

type _ImageTypes = Literal["avatar", "banner"]

# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻
# /server personalize Logic
# ⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻


@final
class _FontSelect(Select["_PersonalizationView"]):
    def __init__(self) -> None:
        super().__init__(
            placeholder = "Select a font...",
            options     = [
                SelectOption(label = label, value = value, description = description, emoji = emoji)
                for label, description, value, emoji in FONT_OPTIONS
            ],
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        if not self.view:
            return

        await self.view.apply(interaction, font = DisplayNameFont[self.values[0]])


@final
class _EffectSelect(Select["_PersonalizationView"]):
    def __init__(self) -> None:
        super().__init__(
            placeholder = "Select an effect...",
            options     = [SelectOption(label = label, value = value) for label, value in EFFECT_OPTIONS],
        )

    @override
    async def callback(self, interaction : Interaction) -> None:
        if not self.view:
            return

        await self.view.apply(interaction, effect = DisplayNameEffect[self.values[0]])


@final
class _ColorsModal(Modal, title = "Edit Color(s)"):
    def __init__(self, view : _PersonalizationView) -> None:
        super().__init__()
        self.view = view

        colors = "-".join(view.style.colors)

        self._colors = TextInput[Self](
            placeholder = "ABCDEF or ABCDEF-123456",
            default     = colors,
            min_length  = 6,
            max_length  = 13,
        )
        self.colors  = Label[Self](
            text        = "Color(s)",
            description = "The display name's color(s), as hex without the #.",
            component   = self._colors,
        )

        self.add_items(self.colors)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        value     = self._colors.value.strip()
        gradient  = self.view.style.effect_id == DisplayNameEffect.gradient
        color_set = value.split("-")

        if not COLOR_PATTERN.match(value) or (not gradient and len(color_set) > 1):
            error = (
                "Gradient must be of the form `ABCDEF-123456`."
                if gradient else
                "Color must be of the form `ABCDEF`."
            )

            await send_bad_argument(
                interaction,
                title    = "set display name colors",
                subtitle = {"colors" : error},
            )
            return

        await self.view.apply(interaction, colors = color_set)


@final
class _ColorsButton(Button["_PersonalizationView"]):
    def __init__(self) -> None:
        super().__init__(label = "Edit Colors")

    @override
    async def callback(self, interaction : Interaction) -> None:
        if not self.view:
            return

        await interaction.response.send_modal(_ColorsModal(self.view))


@final
class _ImageModal(Modal):
    def __init__(self, view : _PersonalizationView, target : _ImageTypes) -> None:
        super().__init__(title = f"Edit {target.title()}")
        self.view   = view
        self.target = target

        self._upload = FileUpload[Self](required = False)
        self.upload  = Label[Self](
            text        = target.title(),
            description = f"The new {target} image (PNG, JPG, or GIF).",
            component   = self._upload,
        )

        self._reset = Checkbox[Self]()
        self.reset  = Label[Self](
            text        =  "Reset",
            description = f"Whether to remove the current {target} instead of uploading one.",
            component   = self._reset,
        )

        self.add_items(self.upload, self.reset)

    @override
    async def on_submit(self, interaction : Interaction) -> None:
        guild = interaction.guild
        if not guild:
            return

        me = guild.me
        if not me:
            return

        reset      = self._reset.value
        attachment = self._upload.values[0] if self._upload.values else None

        if not reset and attachment is None:
            await send_bad_argument(
                interaction,
                title    = f"set {self.target}",
                subtitle = {None : f"Upload an image or choose to reset the {self.target}."},
            )
            return

        if not reset and attachment is not None and not (attachment.content_type or "").startswith("image/"):
            await send_bad_argument(
                interaction,
                title    = f"set {self.target}",
                subtitle = {None : "The file must be an image."},
            )
            return

        try:
            data = await attachment.read() if attachment is not None and not reset else None
            if self.target == "avatar":
                member = await me.edit(avatar = data)
            else:
                member = await me.edit(banner = data)
        except HTTPException as e:
            await send_bad_operation(
                interaction,
                title    = f"set {self.target}",
                subtitle = codeblock(e),
            )
            return

        if not member:
            return

        if self.target == "avatar":
            self.view.avatar_url = member.guild_avatar.url if member.guild_avatar else None
        if self.target == "banner":
            self.view.banner_url = member.guild_banner.url if member.guild_banner else None

        self.view.update_pages()

        await interaction.response.edit_message(view = self.view)


@final
class _ImageButton(Button["_PersonalizationView"]):
    def __init__(self, target : _ImageTypes) -> None:
        super().__init__(label = f"Edit {target.title()}")
        self.target : _ImageTypes = target

    @override
    async def callback(self, interaction : Interaction) -> None:
        if not self.view:
            return

        await interaction.response.send_modal(_ImageModal(self.view, self.target))


@final
class _PersonalizationView(NamedPaginator):
    def __init__(
        self,
        style      : NameStyleResult,
        *,
        avatar_url : str | None,
        banner_url : str | None,
    ) -> None:
        self.style      = style
        self.avatar_url = avatar_url
        self.banner_url = banner_url

        self.font_select   = _FontSelect()
        self.effect_select = _EffectSelect()
        self.color_button  = _ColorsButton()
        self.avatar_button = _ImageButton("avatar")
        self.banner_button = _ImageButton("banner")

        initial_pages = [
            PageData(name = "Name Style",      content = []),
            PageData(name = "Avatar & Banner", content = []),
        ]

        super().__init__(initial_pages, container = True)
        self.update_pages()

    async def apply(
        self,
        interaction : Interaction,
        *,
        font        : DisplayNameFont   | None = None,
        effect      : DisplayNameEffect | None = None,
        colors      : list[str]         | None = None,
    ) -> None:
        guild = interaction.guild
        if not guild:
            return

        font_id    = font   if font   is not None else self.style.font_id
        effect_id  = effect if effect is not None else self.style.effect_id
        color_list = colors if colors is not None else self.style.colors

        if effect_id == DisplayNameEffect.gradient:
            if len(color_list) == 1:
                color_list = [color_list[0], color_list[0]]
        elif len(color_list) > 1:
            if colors is not None:
                await send_bad_argument(
                    interaction,
                    title    = "set display name style",
                    subtitle = {"colors" : "Only the gradient effect accepts two colors."},
                )
                return

            color_list = color_list[:1]

        try:
            await interaction.client.set_name_style(
                guild,
                font_id   = font_id,
                effect_id = effect_id,
                colors    = color_list,
            )
        except Exception as e:
            await send_bad_operation(
                interaction,
                title    = "set display name style",
                subtitle = codeblock(e),
            )
            return

        updated = await interaction.client.get_name_style(guild)
        if updated:
            self.style = updated

        self.update_pages()

        await interaction.response.edit_message(view = self)

    def update_pages(self) -> None:
        colors = "-".join(f"`{color}`" for color in self.style.colors) or "None"

        for option in self.font_select.options:
            option.default = option.value == self.style.font_id.name

        for option in self.effect_select.options:
            option.default = option.value == self.style.effect_id.name

        s = "s" if len(self.style.colors) > 1 else ""
        txt_colors = (
           f"**Color{s}**\n"
           f"{colors}\n"
            "Set one hex color, or two for a gradient."
        )

        txt_avatar = (
            (
                f"**Avatar**\n"
                f"[View current avatar]({self.avatar_url})"
            ) if self.avatar_url else (
                "**Avatar**\n"
                "No server avatar is set."
            )
        )

        txt_banner = (
            (
                f"**Banner**\n"
                f"[View current banner]({self.banner_url})"
            ) if self.banner_url else (
                "**Banner**\n"
                "No server banner is set."
            )
        )

        self.pages = [
            PageData(
                name    = "Name Style",
                content = [
                    "# Name Style",
                    TextDisplay("**Font**"),
                    ActionRow(self.font_select),
                    TextDisplay("**Effect**"),
                    ActionRow(self.effect_select),
                    ButtonSection(txt_colors, button = self.color_button),
                ],
            ),
            PageData(
                name    = "Avatar & Banner",
                content = [
                    "# Avatar & Banner",
                    ButtonSection(txt_avatar, button = self.avatar_button),
                    ButtonSection(txt_banner, button = self.banner_button),
                ],
            ),
        ]


async def run_server_personalize(interaction : Interaction) -> None:
    """
    Personalize Cordex's avatar, banner, and name style.

    Parameters
    ----------
    interaction : `Interaction`
        The interaction context to run the command with.
    """
    guild = interaction.guild
    if not guild:
        return

    style = await interaction.client.get_name_style(guild)
    if not style:
        return

    me = guild.me
    if not me:
        return

    avatar = me.guild_avatar
    banner = me.guild_banner

    await interaction.response.send_message(
        view      = _PersonalizationView(
            style,
            avatar_url = avatar.url if avatar else None,
            banner_url = banner.url if banner else None,
        ),
        ephemeral = True,
    )
