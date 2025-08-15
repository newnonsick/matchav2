from datetime import datetime
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.datetime_utils import get_date_now
from views.delete_message_view import DeleteMessageView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class LeaveSummary(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(name="leave_summary", description="แสดงสรุปการลา")
    @app_commands.describe(
        hidden="ต้องการซ่อนข้อความนี้หรือไม่",
        date="ระบุวันที่ในรูปแบบ YYYY-MM-DD เพื่อดูข้อมูลของวันนั้น",
    )
    async def leave_summary(
        self,
        interaction: discord.Interaction,
        hidden: Optional[bool] = False,
        date: Optional[str] = None,
    ):
        await interaction.response.defer(ephemeral=hidden if hidden else False)

        if not interaction.guild:
            await interaction.edit_original_response(
                content="คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์เท่านั้น"
            )
            return

        if not date:
            target_date = get_date_now()
        else:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                await interaction.edit_original_response(
                    content="วันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD"
                )
                return

        leaves = await self.client.leave_service.get_daily_leaves(target_date)
        embed = await self.client.leave_service.get_daily_leaves_embed(
            leaves, target_date
        )

        await interaction.edit_original_response(
            content="",
            embed=embed,
            view=DeleteMessageView(parent_interaction=interaction),
        )


async def setup(client: "CustomBot"):
    await client.add_cog(LeaveSummary(client))
