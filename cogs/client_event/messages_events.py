from datetime import datetime

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
            try:
                await self.client.standup_service.track_standup(message, check=False)
                await message.add_reaction("✅")
            except ValueError as e:
                print(f"ValueError: {e}")
                await message.add_reaction("❌")
            except Exception as e:
                print(f"Error tracking stand-up message: {e}")
                await message.add_reaction("❌")

        elif message.channel.id in DataCache.ATTENDANCE_CHANNELS:
            try:
                leave_request: list = await self.client.leave_service.track_leave(
                    message
                )
                await self.client.leave_service.send_leave_confirmation(
                    leave_request, message
                )
                await message.add_reaction("😎")
            except ValueError as e:
                print(f"ValueError: {e}")
                await message.add_reaction("❌")
            except Exception as e:
                print(f"Error tracking leave message: {e}")
                await message.add_reaction("❌")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.channel.id in DataCache.STANDUP_CHANNELS:
            try:
                await self.client.standup_service.delete_standup_by_message_id(
                    message.id
                )
            except Exception as e:
                print(f"Error deleting stand-up message: {e}")

        elif message.channel.id in DataCache.ATTENDANCE_CHANNELS:
            try:
                await self.client.leave_service.delete_leave_by_message_id(message.id)
                await self.client.leave_service.send_leave_deletion_notification(
                    message
                )
            except Exception as e:
                print(f"Error deleting leave message: {e}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild:
            return

        if before.channel.id in DataCache.STANDUP_CHANNELS:
            updated_msg = await after.channel.fetch_message(after.id)
            try:
                await self.client.standup_service.delete_standup_by_message_id(
                    before.id
                )
                await self.client.standup_service.track_standup(after, check=False)
                await clear_bot_reactions(updated_msg, self.client)
                await after.add_reaction("✅")
            except ValueError as e:
                print(f"ValueError: {e}")
                await clear_bot_reactions(updated_msg, self.client)
                await after.add_reaction("❌")
            except Exception as e:
                print(f"Error tracking stand-up message: {e}")
                await clear_bot_reactions(updated_msg, self.client)
                await after.add_reaction("❌")

        elif before.channel.id in DataCache.ATTENDANCE_CHANNELS:
            updated_msg = await after.channel.fetch_message(after.id)
            try:
                await self.client.leave_service.delete_leave_by_message_id(before.id)
                leave_request: list = await self.client.leave_service.track_leave(after)
                await self.client.leave_service.send_edit_leave_comfirmation(leave_request, after)
                await clear_bot_reactions(updated_msg, self.client)
                await after.add_reaction("😎")
            except ValueError as e:
                print(f"ValueError: {e}")
                await clear_bot_reactions(updated_msg, self.client)
                await after.add_reaction("❌")
            except Exception as e:
                print(f"Error tracking leave message: {e}")
                await clear_bot_reactions(updated_msg, self.client)
                await after.add_reaction("❌")


async def setup(client: CustomBot):
    await client.add_cog(MessagesEvents(client))
