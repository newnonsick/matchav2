import discord
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands

from config import LEAVE_SUMMARY_CHANNEL_ID
from core.custom_bot import CustomBot
from datacache import DataCache
from utils.datetime_utils import get_date_now, get_datetime_range


class DailySummarySchedulerCog(commands.Cog):
    def __init__(self, client: CustomBot):
        self.client = client
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Bangkok"))
        self.scheduler.add_job(
            self.send_standup, trigger="cron", day_of_week="mon-fri", hour=9, minute=30
        )
        self.scheduler.add_job(
            self.send_leave, trigger="cron", day_of_week="mon-fri", hour=9, minute=30
        )
        self.scheduler.start()

    async def send_leave(self):
        date = get_date_now()
        embed = await self.client.leave_service.get_daily_leaves_embed(date)
        channel_id = LEAVE_SUMMARY_CHANNEL_ID
        channel = self.client.get_channel(channel_id)
        if channel and isinstance(channel, discord.TextChannel):
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                print(f"Cannot send message to channel {channel_id}: Forbidden")
            except Exception as e:
                print(f"Error sending leave summary to channel {channel_id}: {e}")

    async def send_standup(self):
        date = get_date_now()
        from_datetime, to_datetime = get_datetime_range(date)
        for channel_id in DataCache.STANDUP_CHANNELS:
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
                    await channel.send(
                        embed=embed,
                    )
                except discord.Forbidden:
                    print(f"Cannot send message to channel {channel_id}: Forbidden")
                except Exception as e:
                    print(f"Error sending reminder to channel {channel_id}: {e}")


async def setup(client: CustomBot):
    await client.add_cog(DailySummarySchedulerCog(client))
