from datetime import date, datetime
from typing import TYPE_CHECKING

import discord
from typing_extensions import Literal

from config import ATTENDANCE_STATUS_EMOTE_MAP, THAI_STATUS_MAP
from models import DailyVoiceAttendance

if TYPE_CHECKING:
    from core.custom_bot import CustomBot
    from repositories.voice_attendance_repository import VoiceAttendanceRepository


class VoiceAttendanceService:
    def __init__(
        self,
        voice_attendance_repository: "VoiceAttendanceRepository",
        client: "CustomBot",
    ):
        self.voice_attendance_repository = voice_attendance_repository
        self.client = client

    async def get_daily_voice_attendance_embed(
        self,
        attendance_summary: list[DailyVoiceAttendance],
        date: date,
        channel_id: int,
    ) -> discord.Embed:

        embed = discord.Embed(
            title=f"📢 Voice Attendance Summary {date} <#{channel_id}>",
            color=discord.Color.blue(),
        )

        if not attendance_summary:
            embed.description = "No voice attendance records for today."
            return embed

        attendance_summary_text_list = []

        total_ontime = 0
        total_late = 0
        total_absent = 0
        total_leave = 0

        for record in attendance_summary:
            status_emoji = ATTENDANCE_STATUS_EMOTE_MAP.get(record.status, "")
            attendance_summary_text_list.append(
                f"- <@{record.author_id}> {status_emoji}"
            )
            if record.status == "on_time":
                total_ontime += 1
            elif record.status == "late":
                total_late += 1
            elif record.status == "absent":
                total_absent += 1
            elif record.status == "leave":
                total_leave += 1

        batch_size = 25
        for i in range(0, len(attendance_summary_text_list), batch_size):
            batch = attendance_summary_text_list[i : i + batch_size]
            embed.add_field(
                name=f"Members",
                value="\n".join(batch),
                inline=True,
            )

        stats = [
            ("👥 Total Members", len(attendance_summary)),
            (f"{ATTENDANCE_STATUS_EMOTE_MAP.get("on_time", "")} On Time", total_ontime),
            (f"{ATTENDANCE_STATUS_EMOTE_MAP.get("late", "")} Late", total_late),
            (f"{ATTENDANCE_STATUS_EMOTE_MAP.get("absent", "")} Absent", total_absent),
            (f"{ATTENDANCE_STATUS_EMOTE_MAP.get("leave", "")} Leave (Fullday & Morning)", total_leave),
        ]

        stats_text = "\n".join([f"{name}: **{count}**" for name, count in stats])
        embed.add_field(
            name="Attendance Stats",
            value=stats_text,
            inline=False,
        )

        embed.set_footer(
            text=f"Made with ❤️ by TN Backend Min",
        )

        return embed

    async def insert_voice_log(
        self, author_id: str, event_time: datetime, event_type: str, date: date
    ) -> None:
        if event_type not in ["join", "leave"]:
            raise ValueError("event_type must be either 'join' or 'leave'")

        await self.voice_attendance_repository.insert_voice_log(
            author_id, event_time, event_type, date
        )

    async def get_lested_event_type_by_author_id(
        self, author_id: int
    ) -> Literal["join", "leave"] | None:
        return (
            await self.voice_attendance_repository.get_lested_event_type_by_author_id(
                author_id
            )
        )

    async def get_daily_attendance_summary_by_channel_id_and_date(
        self, channel_id: int, date: date
    ) -> list[DailyVoiceAttendance]:
        response = await self.voice_attendance_repository.get_daily_attendance_summary_by_channel_id_and_date(
            channel_id, date
        )
        return response
