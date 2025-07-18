from discord.ext import commands
from core.custom_bot import CustomBot
from discord import app_commands
import discord

from datacache import DataCache

class Register(commands.Cog):

    def __init__(self, client: CustomBot):
        self.client = client

    @app_commands.command(name="register", description="เพิ่มทีม stand-up")
    async def register(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("คำสั่งนี้ใช้ได้เฉพาะในเซิร์ฟเวอร์เท่านั้น", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        if interaction.channel is None or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.edit_original_response(content="คำสั่งนี้ใช้ได้เฉพาะในช่องข้อความเท่านั้น")
            return

        if interaction.channel.id in DataCache.STANDUP_CHANNELS:
            await interaction.edit_original_response(content="ช่องนี้ได้ลงทะเบียนไว้แล้ว")
            return

        await self.client.standup_service.regis_new_standup_channel(
            channel_id=interaction.channel.id,
            team_name=interaction.channel.name,
            server_id=interaction.guild.id,
            server_name=interaction.guild.name,
            timestamp=interaction.created_at.isoformat()
        )
        DataCache.STANDUP_CHANNELS.append(interaction.channel.id)
        await interaction.edit_original_response(content="ช่องนี้ได้ลงทะเบียนเป็นช่อง Stand-Up เรียบร้อยแล้ว")

async def setup(client: CustomBot):
    await client.add_cog(Register(client))
