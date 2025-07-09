import discord
from discord import app_commands
from discord.ext import commands

from core.custom_bot import CustomBot
from datacache import DataCache


class Track(commands.Cog):

    def __init__(self, client: CustomBot):
        self.client = client

    @app_commands.command(name="track", description="เพิ่มการติดตาม Stand-Up Message")
    @app_commands.describe(
        message_id='ID ของ Stand-up Message ที่ต้องการติดตาม โดยคลิกขวาที่ข้อความแล้วเลือก "Copy Message ID"',
    )
    async def track(self, interaction: discord.Interaction, message_id: str):
        await interaction.response.defer(ephemeral=True)
        if not interaction.guild:
            await interaction.edit_original_response(
                content="คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์เท่านั้น"
            )
            return

        channel = interaction.channel
        if isinstance(channel, discord.TextChannel):
            if channel.id not in DataCache.STANDUP_CHANNELS:
                await interaction.edit_original_response(content="ช่องนี้ไม่ใช่ช่อง Stand-Up")
                return
            message: discord.Message = await channel.fetch_message(int(message_id))
        else:
            await interaction.response.send_message(
                "This command can only be used in text channels.", ephemeral=True
            )
            return

        if not message:
            await interaction.edit_original_response(content="ไม่พบข้อความที่ระบุ")
            return

        try:
            await self.client.standup_service.track_standup(message)
            await interaction.edit_original_response(
                content="ติดตาม Stand-Up Message เรียบร้อยแล้ว"
            )
        except ValueError as e:
            await interaction.edit_original_response(content=str(e))
        except Exception as e:
            await interaction.edit_original_response(content=f"เกิดข้อผิดพลาด: {str(e)}")
            print(f"Error tracking stand-up message: {e}")


async def setup(client: CustomBot):
    await client.add_cog(Track(client))
