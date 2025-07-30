from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from config import MATCHA_HELP_IMG_URL
from views.help_view import HelpView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class Help(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(name="help", description="Get help with the bot commands.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🍵 Welcome to Matcha Bot!",
            description="""Hey there! I'm Matcha Bot, your friendly assistant for managing daily stand-ups and leave requests. I'm here to streamline your team's communication and keep everyone in sync. 

Ready to explore what I can do? Use the dropdown menu below to navigate through my commands.

✨ **Select a category to get started!**
""",
            color=discord.Color.from_rgb(64, 224, 208),
        ).set_image(url=MATCHA_HELP_IMG_URL)
        view = HelpView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(client: "CustomBot"):
    await client.add_cog(Help(client))
