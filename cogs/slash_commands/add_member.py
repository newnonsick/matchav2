from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from datacache import DataCache
from utils.datetime_utils import get_datetime_now
from utils.decorators import is_admin

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class AddMember(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(name="add_member", description="เพิ่มสมาชิกในทีม Stand-Up")
    @app_commands.describe(user="สมาชิก")
    @is_admin()
    async def add_member(self, interaction: discord.Interaction, user: discord.User):
        if not interaction.guild:
            await interaction.response.send_message(
                "คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์เท่านั้น", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        if interaction.channel is None or not isinstance(
            interaction.channel, discord.TextChannel
        ):
            await interaction.edit_original_response(
                content="คำสั่งนี้ใช้ได้เฉพาะในช่องข้อความเท่านั้น"
            )
            return

        if interaction.channel.id not in DataCache.STANDUP_CHANNELS:
            await interaction.edit_original_response(content="ช่องนี้ไม่ใช่ช่อง Stand-Up")
            return

        try:
            channel_id = interaction.channel.id
            user_id = user.id
            user_name = user.display_name if user.display_name else user.name
            created_at = get_datetime_now()

            await self.client.member_service.add_member_to_standup_channel(
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                created_at=created_at,
            )
            await interaction.edit_original_response(
                content=f"เพิ่มสมาชิก <@{user.id}> เรียบร้อยแล้ว"
            )
        except ValueError as e:
            await interaction.edit_original_response(content=str(e))
        except Exception as e:
            await interaction.edit_original_response(content=f"เกิดข้อผิดพลาด: {str(e)}")


async def setup(client: "CustomBot"):
    await client.add_cog(AddMember(client))
