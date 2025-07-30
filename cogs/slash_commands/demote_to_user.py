from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.decorators import is_admin

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class DemoteToUser(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(
        name="demote_to_user", description="Demote an admin to a regular user"
    )
    @app_commands.describe(user="The user to demote to a regular user")
    @is_admin()
    async def demote_to_user(
        self, interaction: discord.Interaction, user: discord.User
    ):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            await interaction.edit_original_response(
                content="This command can only be used in a server."
            )
            return

        try:
            await self.client.member_service.demote_admin_to_user(user.id)
        except ValueError as e:
            await interaction.edit_original_response(content=str(e))
            return
        except Exception as e:
            await interaction.edit_original_response(
                content=f"An error occurred: {str(e)}"
            )
            return

        await interaction.edit_original_response(
            content=f"{user.mention} has been demoted to a regular user."
        )


async def setup(client: "CustomBot"):
    await client.add_cog(DemoteToUser(client))
