from typing import TYPE_CHECKING
from uuid import UUID

import discord
from discord import app_commands
from discord.ext import commands

from config import TASK_STATUS_MAP
from views.standup_task_update_view import StandupTaskUpdateView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class UpdateTaskStatus(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(
        name="update_task_status", description="Update the status of a task"
    )
    @app_commands.describe(
        task_id="The ID of the task to update",
    )
    async def update_task_status(self, interaction: discord.Interaction, task_id: str):
        try:
            task_uuid = UUID(task_id)
        except ValueError:
            await interaction.response.send_message(
                "Invalid task ID format. Please provide a valid UUID.", ephemeral=True
            )
            return

        task = await self.client.standup_service.get_task_by_id(task_uuid)
        if not task or task.author_id != str(interaction.user.id):
            await interaction.response.send_message(
                "You do not have permission to update this task or the task does not exist.",
                ephemeral=True,
            )
            return

        view = StandupTaskUpdateView(
            task=task, client=self.client, is_first=False, timeout=180
        )
        await interaction.response.send_message(
            content=(
                "You have 3 minutes to update the task status.\n\n"
                f"**Task ID:** {task.id}\n"
                f"**Task:** {task.task}\n"
                f"**Status:** {TASK_STATUS_MAP.get(task.status)}\n"
            ),
            view=view,
            ephemeral=True,
        )


async def setup(client: "CustomBot"):
    await client.add_cog(UpdateTaskStatus(client))
