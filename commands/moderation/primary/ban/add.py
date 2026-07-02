from bot import Interaction


async def run_mod_primary_ban_add(interaction : Interaction) -> None:
    await interaction.response.send_message("You shouldn't be able to see this!")
