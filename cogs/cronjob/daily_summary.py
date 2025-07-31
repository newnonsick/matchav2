import asyncio
from typing import TYPE_CHECKING

import discord
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

from config import LEAVE_SUMMARY_CHANNEL_ID, OFFICE_ENTRY_SUMMARY_CHANNEL_ID
from datacache import DataCache
from utils.datetime_utils import get_date_now, get_datetime_range

if TYPE_CHECKING:
    from core.custom_bot import CustomBot


class DailySummarySchedulerCog(commands.Cog):
    def __init__(self, client: "CustomBot"):
        self.client = client
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Bangkok"))
        self.scheduler.add_job(
            self.send_standup, trigger="cron", day_of_week="mon-fri", hour=9, minute=30
        )
        self.scheduler.add_job(
            self.send_leave, trigger="cron", day_of_week="mon-fri", hour=9, minute=30
        )
        self.scheduler.add_job(
            self.send_office_entry,
            trigger="cron",
            day_of_week="mon-fri",
            hour=9,
            minute=30,
        )
        self.scheduler.add_job(
            self.clear_inactive_standup_members,
            trigger="cron",
            day_of_week="mon-fri",
            hour=18,
            minute=30,
        )
        self.scheduler.start()

    async def send_leave(self):
        date = get_date_now()
        leaves = await self.client.leave_service.get_daily_leaves(date)
        embed = await self.client.leave_service.get_daily_leaves_embed(leaves, date)
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

    async def send_standup(self):
        date = get_date_now()
        from_datetime, to_datetime = get_datetime_range(date)

        channel_ids = DataCache.STANDUP_CHANNELS
        BATCH_SIZE = 10
        DELEY_SECONDS = 2

        async def process_channel(channel_id):
            channel = self.client.get_channel(channel_id)
            if channel and isinstance(channel, discord.TextChannel):
                try:
                    userid_wrote_standup = (
                        await self.client.standup_service.get_userid_wrote_standup(
                            channel_id, from_datetime, to_datetime
                        )
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

    async def send_office_entry(self):
        date = get_date_now()
        entries = await self.client.office_entry_service.get_daily_office_entries(date)
        embed = await self.client.office_entry_service.get_daily_office_entries_embed(
            entries, date
        )
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


async def setup(client: "CustomBot"):
    await client.add_cog(DailySummarySchedulerCog(client))
