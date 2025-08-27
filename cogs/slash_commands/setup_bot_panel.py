from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.decorators import is_admin
from views.bot_panel_view import BotPanelView
from views.setup_bot_panel_qt_view import SetupBotPanelQuestionView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class SetupBotPanel(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(
        name="setup_bot_panel",
        description="Set up the bot panel in the current channel",
    )
    @is_admin()
    async def setup_bot_panel(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "🚫 This command can only be used in a server!", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        is_panel_existing = await self.client.bot_panel_service.get_bot_panel()
        if is_panel_existing:
            await interaction.edit_original_response(
                content="Setup already complete. Setup again?",
                view=SetupBotPanelQuestionView(client=self.client, interaction=interaction),
            )
        else:
            await self.client.bot_panel_service.setup_bot_panel(interaction=interaction)


async def setup(client: "CustomBot"):
    await client.add_cog(SetupBotPanel(client))
