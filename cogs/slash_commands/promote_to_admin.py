from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.decorators import is_admin

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class PromoteToAdmin(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(
        name="promote_to_admin", description="Promote a user to admin"
    )
    @app_commands.describe(user="The user to promote to admin")
    @is_admin()
    async def promote_to_admin(
        self, interaction: discord.Interaction, user: discord.User
    ):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild:
            await interaction.edit_original_response(
                content="This command can only be used in a server."
            )
            return

        try:
            await self.client.member_service.promote_user_to_admin(user.id)
            await interaction.edit_original_response(
                content=f"{user.mention} has been promoted to admin."
            )
        except ValueError as e:
            await interaction.edit_original_response(content=str(e))
            return
        except Exception as e:
            await interaction.edit_original_response(
                content=f"An error occurred: {str(e)}"
            )
            return


async def setup(client: "CustomBot"):
    await client.add_cog(PromoteToAdmin(client))
