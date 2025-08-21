from datetime import datetime
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

from datacache import DataCache
from utils.datetime_utils import get_date_now, get_datetime_range
from views.delete_message_view import DeleteMessageView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class Team(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(name="team", description="แสดงรายละเอียดทีม")
    @app_commands.describe(
        hidden="ต้องการซ่อนข้อความนี้หรือไม่",
        date="ระบุวันที่ในรูปแบบ YYYY-MM-DD เพื่อดูข้อมูลของวันนั้น",
    )
    async def team(
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

        channel_id = interaction.channel.id if interaction.channel is not None else None

        if channel_id is None:
            await interaction.edit_original_response(content="ไม่สามารถดึงข้อมูลจากช่องนี้ได้")
            return

        if channel_id not in DataCache.STANDUP_CHANNELS:
            await interaction.edit_original_response(content="ช่องนี้ไม่ใช่ช่อง Stand-Up")
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

        # from_datetime, to_datetime = get_datetime_range(target_date)

        userid_wrote_standup = (
            await self.client.standup_service.get_userid_wrote_standup_by_date(
                channel_id, target_date, target_date
            )
        )

        userid_in_standup_channel = (
            await self.client.standup_service.userid_in_standup_channel(channel_id)
        )

        user_inleaves = await self.client.leave_service.get_user_inleave(
            channel_id, target_date
        )

        embed = await self.client.standup_service.get_standup_embed(
            user_inleaves=user_inleaves,
            userid_in_standup_channel=userid_in_standup_channel,
            userid_wrote_standup=userid_wrote_standup,
            channel_id=channel_id,
            date=target_date,
        )

        await interaction.edit_original_response(
            content="",
            embed=embed,
            view=DeleteMessageView(parent_interaction=interaction),
        )


async def setup(client: "CustomBot"):
    await client.add_cog(Team(client))
