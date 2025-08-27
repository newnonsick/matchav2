from typing import TYPE_CHECKING

import discord

from config import TASK_STATUS_MAP
from models import StandupTask

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class SetupBotPanelQuestionView(discord.ui.View):
    def __init__(
        self, client: "CustomBot", interaction: discord.Interaction, timeout: int = 180
    ):
        super().__init__(timeout=timeout)
        self.client = client
        self.interaction = interaction

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        bot_panel = await self.client.bot_panel_service.get_bot_panel()
        if bot_panel is not None:
            await self.client.bot_panel_service.delete_bot_panel()
        await self.client.bot_panel_service.setup_bot_panel(
            interaction=self.interaction
        )
        await interaction.response.edit_message(
            content="✅ The Control Panel has been set up successfully!", view=None
        )
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="Setup cancelled. If you want to set up again, use `/setup`.",
            view=None,
        )
        self.stop()
