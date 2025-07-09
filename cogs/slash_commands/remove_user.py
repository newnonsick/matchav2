import discord
from discord import app_commands
from discord.ext import commands

from core.custom_bot import CustomBot
from datacache import DataCache


class RemoveUser(commands.Cog):

    def __init__(self, client: CustomBot):
        self.client = client

    @app_commands.command(name="remove_user", description="ลบสมาชิกออกจากช่อง Stand-Up")
    @app_commands.describe(user="สมาชิกที่ต้องการลบออก")
    async def remove_user(self, interaction: discord.Interaction, user: discord.User):
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

            await self.client.standup_service.remove_member_from_standup_channel(
                channel_id, user_id
            )
            await interaction.edit_original_response(
                content=f"ลบสมาชิก <@{user.id}> ออกจากช่อง Stand-Up เรียบร้อยแล้ว"
            )
        except ValueError as e:
            await interaction.edit_original_response(content=str(e))
        except Exception as e:
            await interaction.edit_original_response(content=f"เกิดข้อผิดพลาด: {str(e)}")

async def setup(client: CustomBot):
    await client.add_cog(RemoveUser(client))
