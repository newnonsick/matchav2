from typing import TYPE_CHECKING

import discord

from config import TASK_STATUS_MAP
from models import StandupTask

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class StandupTaskUpdateView(discord.ui.View):

    def __init__(self, task: StandupTask, client: "CustomBot", is_latest: bool = False):
        super().__init__(timeout=45000)
        self.task = task
        self.client = client
        self.is_latest = is_latest

    @discord.ui.button(label="Todo", style=discord.ButtonStyle.red)
    async def todo_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.task.id is not None:
            await self.client.standup_service.update_task_status(
                task_id=self.task.id, status="todo"
            )
            await interaction.response.edit_message(
                content=(
                    f"**Task ID:** {self.task.id}\n"
                    f"**Task:** {self.task.task}\n"
                    f"**Status:** Todo\n"
                    f"{"---------------------------------------------------" if not self.is_latest else ""}"
                ),
                view=None,
            )
        else:
            await interaction.response.edit_message(
                content="Error: Task ID is missing and cannot update status.",
                view=None,
            )
        self.stop()

    @discord.ui.button(label="In Progress", style=discord.ButtonStyle.primary)
    async def in_progress_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.task.id is not None:
            await self.client.standup_service.update_task_status(
                task_id=self.task.id, status="in_progress"
            )
            await interaction.response.edit_message(
                content=(
                    f"**Task ID**: {self.task.id}\n"
                    f"**Task** {self.task.task}\n"
                    f"**Status**: In Progress\n"
                    f"{"---------------------------------------------------" if not self.is_latest else ""}"
                ),
                view=None,
            )
        else:
            await interaction.response.edit_message(
                content="Error: Task ID is missing and cannot update status.",
                view=None,
            )
        self.stop()

    @discord.ui.button(label="Done", style=discord.ButtonStyle.green)
    async def done_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.task.id is not None:
            await self.client.standup_service.update_task_status(
                task_id=self.task.id, status="done"
            )
            await interaction.response.edit_message(
                content=(
                    f"**Task ID**: {self.task.id}\n"
                    f"**Task** {self.task.task}\n"
                    f"**Status**: Done\n"
                    f"{"---------------------------------------------------" if not self.is_latest else ""}"
                ),
                view=None,
            )
        else:
            await interaction.response.edit_message(
                content="Error: Task ID is missing and cannot update status.",
                view=None,
            )
        self.stop()

    async def on_timeout(self):
        self.stop()
