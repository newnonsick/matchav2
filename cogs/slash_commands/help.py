import discord
from discord import app_commands
from discord.ext import commands

from core.custom_bot import CustomBot


class Help(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client: CustomBot = client

    @app_commands.command(name="help", description="Get help with the bot commands.")
    async def help(self, interaction: discord.Interaction):
        pass


async def setup(client: CustomBot):
    await client.add_cog(Help(client))
