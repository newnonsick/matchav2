import asyncio
from typing import TYPE_CHECKING

import discord
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

from config import (
    DAILY_VOICE_ATTENDANCE_CHANNEL_ID,
    LEAVE_SUMMARY_CHANNEL_ID,
    OFFICE_ENTRY_SUMMARY_CHANNEL_ID,
    TASK_STATUS_MAP,
)
from datacache import DataCache
from utils.datetime_utils import (
    get_date_now,
    get_datetime_now,
    get_datetime_range,
    get_previous_weekdays,
)
from views.standup_task_update_view import StandupTaskUpdateView

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class DailySummarySchedulerCog(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Bangkok"))
        self.scheduler.add_job(
            self.send_standup, trigger="cron", day_of_week="mon-fri", hour=9, minute=0
        )
        self.scheduler.add_job(
            self.send_leave, trigger="cron", day_of_week="mon-fri", hour=9, minute=0
        )
        self.scheduler.add_job(
            self.send_office_entry,
            trigger="cron",
            day_of_week="mon-fri",
            hour=9,
            minute=0,
        )
        self.scheduler.add_job(
            self.clear_inactive_standup_members,
            trigger="cron",
            day_of_week="mon-fri",
            hour=18,
            minute=30,
        )
        self.scheduler.add_job(
            self.send_daily_voice_attendance,
            trigger="cron",
            day_of_week="mon-fri",
            hour=9,
            minute=30,
            second=1,
        )
        self.scheduler.add_job(
            self.send_previous_standup_remarks,
            trigger="cron",
            day_of_week="mon-fri",
            hour=6,
            minute=0,
        )
        self.scheduler.start()

    async def send_previous_standup_remarks(self):
        current_date = get_date_now()

        if await self.client.company_service.is_holiday_date(current_date):
            return

        target_date = get_previous_weekdays(current_date, num_days=2)[-1]
        while await self.client.company_service.is_holiday_date(target_date):
            target_date = get_previous_weekdays(target_date, num_days=2)[-1]

        all_user_in_standup = await self.client.member_service.get_all_standup_members()

        now = get_datetime_now()
        end_task_datetime = now.replace(hour=18, minute=30, second=0, microsecond=0)
        unix_timestamp = int(end_task_datetime.timestamp())

        print(f"Sending stand-up update for {target_date} to all members...")

        for user in all_user_in_standup:
            try:
                user_standup_tasks = await self.client.standup_service.get_standup_tasks_by_user_and_date(
                    author_id=user.author_id, from_date=target_date, to_date=target_date
                )
                if not user_standup_tasks:
                    continue
                discord_user = await self.client.fetch_user(int(user.author_id))
                await discord_user.send(
                    f"📅 **Stand-Up Update for {target_date}**\n\n"
                    f"Please update your tasks before <t:{unix_timestamp}:R>.\n"
                    "Any tasks not updated will automatically be marked as **todo**.\n"
                    f"**Note:** You can update your tasks by use `/update-task-status <task_id>`\n\n"
                    f"Here are your stand-up tasks from {target_date}:\n\n"
                )
                for i, task in enumerate(user_standup_tasks):
                    await discord_user.send(
                        content=(
                            f"{"---------------------------------------------------" if i else ''}\n"
                            f"**Task ID:** {task.id}\n"
                            f"**Task:** {task.task}\n"
                            f"**Status:** {TASK_STATUS_MAP.get(task.status)}\n"
                        ),
                        view=StandupTaskUpdateView(task=task, client=self.client),
                    )

            except discord.Forbidden:
                print(f"Cannot send DM to {user.server_name}: Forbidden")
            except Exception as e:
                print(f"Error sending stand-up update to {user.server_name}: {e}")

    async def send_daily_voice_attendance(self):
        date = get_date_now()

        if await self.client.company_service.is_holiday_date(date):
            return

        channel_id = DAILY_VOICE_ATTENDANCE_CHANNEL_ID
        channel = self.client.get_channel(channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            await channel.send(f"📢 **Daily Voice Attendance Summary for {date}**")
            try:
                for standup_channel_id in DataCache.STANDUP_CHANNELS:
                    attendance_summary = await self.client.voice_attendance_service.get_daily_attendance_summary_by_channel_id_and_date(
                        standup_channel_id, date
                    )
                    if attendance_summary:
                        embed = await self.client.voice_attendance_service.get_daily_voice_attendance_embed(
                            attendance_summary, date, standup_channel_id
                        )
                        await channel.send(embed=embed)

            except discord.Forbidden:
                print(f"Cannot send message to channel {channel_id}: Forbidden")
            except Exception as e:
                print(
                    f"Error sending daily voice attendance to channel {channel_id}: {e}"
                )

    async def send_leave(self):
        date = get_date_now()

        if await self.client.company_service.is_holiday_date(date):
            return

        leaves = await self.client.leave_service.get_daily_leaves(date)
        embed = await self.client.leave_service.get_daily_leaves_embed(leaves, date)
        if date not in DataCache.daily_leave_summary:
            channel_id = LEAVE_SUMMARY_CHANNEL_ID
            channel = self.client.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                try:
                    message = await channel.send(embed=embed)
                    DataCache.daily_leave_summary = {date: message}
                except discord.Forbidden:
                    print(f"Cannot send message to channel {channel_id}: Forbidden")
                except Exception as e:
                    print(f"Error sending leave summary to channel {channel_id}: {e}")
        else:
            message = DataCache.daily_leave_summary[date]
            try:
                await message.edit(embed=embed)
            except discord.NotFound:
                print(f"Message for date {date} not found, sending new message.")
                channel_id = LEAVE_SUMMARY_CHANNEL_ID
                channel = self.client.get_channel(channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    try:
                        message = await channel.send(embed=embed)
                        DataCache.daily_leave_summary[date] = message
                    except discord.Forbidden:
                        print(f"Cannot send message to channel {channel_id}: Forbidden")
                    except Exception as e:
                        print(
                            f"Error sending leave summary to channel {channel_id}: {e}"
                        )

    async def send_standup(self):
        date = get_date_now()

        if await self.client.company_service.is_holiday_date(date):
            return

        # from_datetime, to_datetime = get_datetime_range(date)

        channel_ids = DataCache.STANDUP_CHANNELS
        BATCH_SIZE = 10
        DELEY_SECONDS = 2

        async def process_channel(channel_id):
            channel = self.client.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                try:
                    userid_wrote_standup = await self.client.standup_service.get_userid_wrote_standup_by_date(
                        channel_id, date, date
                    )
                    userid_in_standup_channel = (
                        await self.client.standup_service.userid_in_standup_channel(
                            channel_id
                        )
                    )
                    user_inleaves = await self.client.leave_service.get_user_inleave(
                        channel_id, date
                    )

                    embed = await self.client.standup_service.get_standup_embed(
                        user_inleaves=user_inleaves,
                        userid_in_standup_channel=userid_in_standup_channel,
                        userid_wrote_standup=userid_wrote_standup,
                        channel_id=channel_id,
                        date=date,
                    )
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    print(f"Cannot send message to channel {channel_id}: Forbidden")
                except Exception as e:
                    print(f"Error sending reminder to channel {channel_id}: {e}")

        for i in range(0, len(channel_ids), BATCH_SIZE):
            batch = channel_ids[i : i + BATCH_SIZE]
            await asyncio.gather(*(process_channel(cid) for cid in batch))
            if i + BATCH_SIZE < len(channel_ids):
                await asyncio.sleep(DELEY_SECONDS)

    async def clear_inactive_standup_members(self):
        date = get_date_now()

        if await self.client.company_service.is_holiday_date(date):
            return

        num_days = 5
        inactive_members = (
            await self.client.standup_service.get_members_inactive_standup(
                num_days=num_days
            )
        )
        if not inactive_members:
            return

        for member in inactive_members:
            try:
                await self.client.member_service.remove_member_from_all_standup_channels(
                    int(member.author_id)
                )
                user = await self.client.fetch_user(int(member.author_id))
                await self.client.member_service.send_standup_removal_notification(
                    member=user,
                    reason=f"Inactive for {num_days} days",
                )
            except discord.NotFound:
                print(f"User {member.author_id} not found, possibly deleted.")
            except discord.Forbidden:
                print(f"Cannot send DM to {member.server_name}: Forbidden")
            except Exception as e:
                print(f"Error removing {member.server_name} from standup: {e}")

        await self.client.member_service.send_standup_removal_to_related_person(
            members=inactive_members,
            reason=f"Inactive for {num_days} days",
        )

    async def send_office_entry(self):
        date = get_date_now()

        if await self.client.company_service.is_holiday_date(date):
            return

        entries = await self.client.office_entry_service.get_daily_office_entries(date)
        embed = await self.client.office_entry_service.get_daily_office_entries_embed(
            entries, date
        )
        if date not in DataCache.daily_office_entry_summary:
            channel_id = OFFICE_ENTRY_SUMMARY_CHANNEL_ID
            channel = self.client.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                try:
                    message = await channel.send(embed=embed)
                    DataCache.daily_office_entry_summary = {date: message}
                except discord.Forbidden:
                    print(f"Cannot send message to channel {channel_id}: Forbidden")
                except Exception as e:
                    print(
                        f"Error sending office entry summary to channel {channel_id}: {e}"
                    )
        else:
            message = DataCache.daily_office_entry_summary[date]
            try:
                await message.edit(embed=embed)
            except discord.NotFound:
                print(f"Message for date {date} not found, sending new message.")
                channel_id = OFFICE_ENTRY_SUMMARY_CHANNEL_ID
                channel = self.client.get_channel(channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    try:
                        message = await channel.send(embed=embed)
                        DataCache.daily_office_entry_summary[date] = message
                    except discord.Forbidden:
                        print(f"Cannot send message to channel {channel_id}: Forbidden")
                    except Exception as e:
                        print(
                            f"Error sending office entry summary to channel {channel_id}: {e}"
                        )


async def setup(client: "CustomBot"):
    await client.add_cog(DailySummarySchedulerCog(client))
