import discord
from discord.ext import commands

from core.custom_bot import CustomBot
from datacache import DataCache
from utils.message_utils import clear_bot_reactions


class MessagesEvents(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.channel.id in DataCache.STANDUP_CHANNELS:
            await clear_bot_reactions(message, self.client)
            try:
                await self.client.standup_service.track_standup(message)
                await message.add_reaction("✅")
            except ValueError as e:
                print(f"ValueError: {e}")
                await message.add_reaction("❌")
            except Exception as e:
                print(f"Error tracking stand-up message: {e}")
                await message.add_reaction("❌")

        elif message.channel.id in DataCache.ATTENDANCE_CHANNELS:
            await clear_bot_reactions(message, self.client)
            try:
                await self.client.leave_service.track_leave(message)
                await message.add_reaction("😎")
            except ValueError as e:
                print(f"ValueError: {e}")
                await message.add_reaction("❌")
            except Exception as e:
                print(f"Error tracking leave message: {e}")
                await message.add_reaction("❌")


async def setup(client: CustomBot):
    await client.add_cog(MessagesEvents(client))
