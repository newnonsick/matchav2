# from datetime import datetime, time
# from typing import TYPE_CHECKING

# import discord
# from discord.ext import commands

# from config import DAILY_VOICE_CHANNEL_ID
# from utils.datetime_utils import get_date_now, get_datetime_now

# if TYPE_CHECKING:
#     from core.custom_bot import CustomBot


# class VoiceEvents(commands.Cog):

#     def __init__(self, client: "CustomBot"):
#         self.client = client

#     @commands.Cog.listener()
#     async def on_voice_state_update(
#         self,
#         member: discord.Member,
#         before: discord.VoiceState,
#         after: discord.VoiceState,
#     ):
#         if member.bot:
#             return

#         now = get_datetime_now()
#         today = get_date_now()

#         # start_time = datetime.combine(today, time(8, 0))
#         # end_time = datetime.combine(today, time(9, 30))

#         # if not (start_time <= now <= end_time):
#         #     return

#         try:

#             if (
#                 after.channel
#                 and after.channel.id == DAILY_VOICE_CHANNEL_ID
#                 and await self.client.voice_attendance_service.get_lested_event_type_by_author_id(
#                     member.id
#                 )
#                 != "join"
#             ):

#                 await self.client.voice_attendance_service.insert_voice_log(
#                     author_id=str(member.id),
#                     event_time=now,
#                     event_type="join",
#                     date=today,
#                 )

#             elif (
#                 before.channel
#                 and before.channel.id == DAILY_VOICE_CHANNEL_ID
#                 and await self.client.voice_attendance_service.get_lested_event_type_by_author_id(
#                     member.id
#                 )
#                 != "leave"
#             ):

#                 await self.client.voice_attendance_service.insert_voice_log(
#                     author_id=str(member.id),
#                     event_time=now,
#                     event_type="leave",
#                     date=today,
#                 )

#         except Exception as e:
#             print(f"Error logging voice state update for {member.id}: {e}")
#             # Optionally, you can log this error to a file or a logging service
#             # await self.client.log_error(f"Voice state update error: {e}")


# async def setup(client: "CustomBot"):
#     await client.add_cog(VoiceEvents(client))
