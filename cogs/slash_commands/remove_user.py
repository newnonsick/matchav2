from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands

from datacache import DataCache
from utils.decorators import is_admin

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class RemoveUser(commands.Cog):

    def __init__(self, client: "CustomBot"):
        self.client = client

    @app_commands.command(name="remove_user", description="ลบสมาชิกออกจากช่อง Stand-Up")
    @app_commands.describe(user="สมาชิกที่ต้องการลบออก")
    @is_admin()
    async def remove_user(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.User] = None,
        user_id: Optional[str] = None,
    ):
        if not interaction.guild:
            await interaction.response.send_message(
                "คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์เท่านั้น", ephemeral=True
            )
            return

        if not user and not user_id:
            await interaction.response.send_message(
                "กรุณาระบุสมาชิกที่ต้องการลบออก", ephemeral=True
            )
            return

        if user and user_id:
            await interaction.response.send_message(
                "กรุณาระบุเพียงหนึ่งในสมาชิกหรือ user_id เท่านั้น", ephemeral=True
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
            if user:
                real_user_id = user.id
            elif user_id:
                if user_id.isdigit():
                    real_user_id = int(user_id)
                else:
                    await interaction.edit_original_response(
                        content="user_id ต้องเป็นตัวเลข"
                    )
                    return

            channel_id = interaction.channel.id

            await self.client.member_service.remove_member_from_standup_channel(
                channel_id, real_user_id
            )
            await interaction.edit_original_response(
                content=f"ลบสมาชิก <@{real_user_id}> ออกจากช่อง Stand-Up เรียบร้อยแล้ว"
            )
        except ValueError as e:
            await interaction.edit_original_response(content=str(e))
        except Exception as e:
            await interaction.edit_original_response(content=f"เกิดข้อผิดพลาด: {str(e)}")


async def setup(client: "CustomBot"):
    await client.add_cog(RemoveUser(client))
