import re
from datetime import datetime
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from config import IGNORED_BOT_IDS
from datacache import DataCache
from models import LeaveInfo
from utils.datetime_utils import compare_date_with_today, get_date_now
from utils.message_utils import clear_bot_reactions

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class MessagesEvents(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author.bot and (message.author.id not in IGNORED_BOT_IDS)) or (
            not message.guild
        ):
            return

        if message.channel.id in DataCache.STANDUP_CHANNELS:
            try:
                time_status = await self.client.standup_service.track_standup(
                    message, check_is_exist=False
                )
                if time_status == "today":
                    await message.add_reaction("✅")
                elif time_status == "future":
                    await message.add_reaction("☑️")
            except ValueError as e:
                print(f"ValueError: {e}")
                await message.add_reaction("❌")
                return
            except Exception as e:
                print(f"Error tracking stand-up message: {e}")
                await message.add_reaction("❌")
                return

            if (
                time_status == "today"
                and self.client.standup_service.is_standup_message_entry_office(
                    message.content
                )
            ):
                await self.client.office_entry_service.update_daily_office_entry_summary()

        elif message.channel.id in DataCache.ATTENDANCE_CHANNELS:
            try:
                leave_request: list[LeaveInfo] = (
                    await self.client.leave_service.track_leave(message)
                )
                await self.client.leave_service.send_leave_confirmation(
                    leave_request, message
                )
                await message.add_reaction("😎")
            except ValueError as e:
                print(f"ValueError: {e}")
                await message.add_reaction("❌")
            except discord.Forbidden as e:
                print(f"Error tracking leave message Forbidden: {message.id} - {e}")
                await message.add_reaction("⭕")
            except Exception as e:
                print(f"Error tracking leave message: {e}")
                await message.add_reaction("❌")

            leave_date = set(leave.absent_date for leave in leave_request)
            current_date = get_date_now()
            if (current_date in DataCache.daily_leave_summary.keys()) and (
                current_date in leave_date
            ):
                await self.client.leave_service.update_daily_leave_summary(current_date)

    # @commands.Cog.listener()
    # async def on_message_delete(self, message: discord.Message):
    #     if message.author.bot or not message.guild:
    #         return

    #     if message.channel.id in DataCache.STANDUP_CHANNELS:
    #         try:
    #             await self.client.standup_service.delete_standup_by_message_id(
    #                 message.id
    #             )
    #         except Exception as e:
    #             print(f"Error deleting stand-up message: {e}")

    #     elif message.channel.id in DataCache.ATTENDANCE_CHANNELS:
    #         try:
    #             await self.client.leave_service.delete_leave_by_message_id(message.id)
    #             await self.client.leave_service.send_leave_deletion_notification(
    #                 message
    #             )
    #         except Exception as e:
    #             print(f"Error deleting leave message: {e}")

    # @commands.Cog.listener()
    # async def on_message_edit(self, before: discord.Message, after: discord.Message):
    #     if before.author.bot or not before.guild:
    #         return

    #     if before.channel.id in DataCache.STANDUP_CHANNELS:
    #         updated_msg = await after.channel.fetch_message(after.id)
    #         try:
    #             await self.client.standup_service.delete_standup_by_message_id(
    #                 before.id
    #             )
    #             await self.client.standup_service.track_standup(after, check=False)
    #             await clear_bot_reactions(updated_msg, self.client)
    #             await after.add_reaction("✅")
    #         except ValueError as e:
    #             print(f"ValueError: {e}")
    #             await clear_bot_reactions(updated_msg, self.client)
    #             await after.add_reaction("❌")
    #         except Exception as e:
    #             print(f"Error tracking stand-up message: {e}")
    #             await clear_bot_reactions(updated_msg, self.client)
    #             await after.add_reaction("❌")

    #     elif before.channel.id in DataCache.ATTENDANCE_CHANNELS:
    #         updated_msg = await after.channel.fetch_message(after.id)
    #         try:
    #             await self.client.leave_service.delete_leave_by_message_id(before.id)
    #             leave_request: list = await self.client.leave_service.track_leave(after)
    #             await self.client.leave_service.send_edit_leave_comfirmation(
    #                 leave_request, after
    #             )
    #             await clear_bot_reactions(updated_msg, self.client)
    #             await after.add_reaction("😎")
    #         except ValueError as e:
    #             print(f"ValueError: {e}")
    #             await clear_bot_reactions(updated_msg, self.client)
    #             await after.add_reaction("❌")
    #         except Exception as e:
    #             print(f"Error tracking leave message: {e}")
    #             await clear_bot_reactions(updated_msg, self.client)
    #             await after.add_reaction("❌")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        if not payload.guild_id:
            return

        message_id = payload.message_id
        channel_id = payload.channel_id

        if (
            channel_id not in DataCache.STANDUP_CHANNELS
            and channel_id not in DataCache.ATTENDANCE_CHANNELS
        ):
            return

        channel = self.client.get_channel(channel_id)
        if not channel:
            return

        if not isinstance(
            channel, (discord.TextChannel, discord.Thread, discord.DMChannel)
        ):
            return

        if channel_id in DataCache.STANDUP_CHANNELS:
            try:
                message = await channel.fetch_message(message_id)
                if not message:
                    return

                if (
                    message.author.bot and (message.author.id not in IGNORED_BOT_IDS)
                ) or not message.guild:
                    return

                pattern = r"\b\d{2}/\d{2}/\d{4}\b"
                message_content = message.content.strip()

                dates = re.findall(pattern, message_content)
                if not dates:
                    raise ValueError(
                        f"Message with ID {message.id} from {message.author.id} does not contain a valid date in the format DD/MM/YYYY."
                    )

                try:
                    message_date = datetime.strptime(dates[0], "%d/%m/%Y").date()
                except ValueError:
                    raise ValueError(
                        f"Message with ID {message.id} from {message.author.id} contains an invalid date format: {dates[0]}. Expected format is DD/MM/YYYY."
                    )

                time_status = compare_date_with_today(message_date)

                if time_status == "past":
                    await clear_bot_reactions(message, self.client)
                    await message.add_reaction("😶")
                    return

                await self.client.standup_service.delete_standup_by_message_id(
                    message.id
                )
                time_status = await self.client.standup_service.track_standup(
                    message, check_is_exist=False, bypass_check_date=True
                )
                await clear_bot_reactions(message, self.client)
                if time_status == "today":
                    await message.add_reaction("✅")
                elif time_status == "future":
                    await message.add_reaction("☑️")
            except ValueError as e:
                print(f"ValueError: {e}")
                await clear_bot_reactions(message, self.client)
                await message.add_reaction("❌")
            except Exception as e:
                print(f"Error tracking stand-up message: {e}")
                await clear_bot_reactions(message, self.client)
                await message.add_reaction("❌")

            await self.client.office_entry_service.update_daily_office_entry_summary()
        elif channel_id in DataCache.ATTENDANCE_CHANNELS:
            try:
                message = await channel.fetch_message(message_id)
                if not message:
                    return

                if (
                    message.author.bot and (message.author.id not in IGNORED_BOT_IDS)
                ) or not message.guild:
                    return

                await self.client.leave_service.delete_leave_by_message_id(message.id)
                leave_request: list[LeaveInfo] = (
                    await self.client.leave_service.track_leave(message)
                )
                await self.client.leave_service.send_edit_leave_comfirmation(
                    leave_request, message
                )
                await clear_bot_reactions(message, self.client)
                await message.add_reaction("😎")
            except ValueError as e:
                print(f"ValueError: {e}")
                await clear_bot_reactions(message, self.client)
                await message.add_reaction("❌")
            except discord.Forbidden as e:
                print(f"Error tracking leave message Forbidden: {message.id} - {e}")
                await message.add_reaction("⭕")
            except Exception as e:
                print(f"Error tracking leave message: {e}")
                await clear_bot_reactions(message, self.client)
                await message.add_reaction("❌")

            await self.client.leave_service.update_daily_leave_summary()

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if not payload.guild_id:
            return

        message_id = payload.message_id
        channel_id = payload.channel_id

        if (
            channel_id not in DataCache.STANDUP_CHANNELS
            and channel_id not in DataCache.ATTENDANCE_CHANNELS
        ):
            return

        channel = self.client.get_channel(channel_id)
        if not channel:
            return

        if not isinstance(
            channel, (discord.TextChannel, discord.Thread, discord.DMChannel)
        ):
            return

        if channel_id in DataCache.STANDUP_CHANNELS:
            try:
                await self.client.standup_service.delete_standup_by_message_id(
                    message_id
                )
            except Exception as e:
                print(f"Error deleting stand-up message: {e}")

            await self.client.office_entry_service.update_daily_office_entry_summary()

        elif channel_id in DataCache.ATTENDANCE_CHANNELS:
            try:
                await self.client.leave_service.delete_leave_by_message_id(message_id)
            except Exception as e:
                print(f"Error deleting leave message: {e}")

            await self.client.leave_service.update_daily_leave_summary()


async def setup(client: "CustomBot"):
    await client.add_cog(MessagesEvents(client))
