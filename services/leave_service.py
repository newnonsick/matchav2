import asyncio
import json

import discord

from repositories.leave_repository import LeaveRepository
from services.gemini_service import GeminiService
from utils.datetime_utils import get_datetime_now


class LeaveService:
    def __init__(
        self, leave_repository: LeaveRepository, gemini_service: GeminiService
    ):
        self.leave_repository: LeaveRepository = leave_repository
        self.gemini_service: GeminiService = gemini_service

    async def get_user_inleave(self, channel_id, date) -> list:

        try:
            response = await self.leave_repository.get_user_inleave(channel_id, date)
            return response
        except Exception as e:
            print(f"Error retrieving user IDs in leave: {e}")
            return []

    async def get_daily_leaves(self, date: str) -> list:
        try:
            response = await self.leave_repository.get_daily_leaves(date)
            return response
        except Exception as e:
            print(f"Error retrieving daily leave: {e}")
            return []

    async def get_daily_leaves_embed(self, date: str) -> discord.Embed:
        response = await self.get_daily_leaves(date)
        team_leaves = {}
        for leave in response:
            if leave["team_name"] not in team_leaves:
                team_leaves[leave["team_name"]] = []

            member_leave = {
                "author_id": leave["author_id"],
                "leave_type": leave["leave_type"],
                "partial_leave": leave["partial_leave"],
            }

            team_leaves[leave["team_name"]].append(member_leave)

        embed = discord.Embed(
            title=f"**📢แจ้งเตือน: พนักงานลาประจำวันนี้ {date}**",
            color=discord.Color.blue(),
        )

        leave_type_map = {
            "annual_leave": "ลาพักร้อน",
            "sick_leave": "ลาป่วย",
            "personal_leave": "ลากิจ",
            "birthday_leave": "ลาวันเกิด",
        }

        partial_leave_map = {
            "afternoon": "ครึ่งบ่าย",
            "morning": "ครึ่งเช้า",
        }

        if not team_leaves:
            embed.description = "ไม่มีพนักงานลาประจำวันนี้"
            return embed

        for team_name, members in team_leaves.items():
            embed.add_field(
                name=f"👶 {team_name}" if "trainee" in team_name else f"🏢 {team_name}",
                value="\n".join(
                    f"<@{member['author_id']}> - {leave_type_map.get(member['leave_type'])} {partial_leave_map.get(member['partial_leave'], '')}"
                    for member in members
                ),
                inline=False,
            )

        return embed

    async def track_leave(self, message: discord.Message) -> None:
        gemini_response = await asyncio.to_thread(
            self.gemini_service.analyze_leave_request, message.content
        )

        if not gemini_response:
            raise ValueError("ไม่สามารถวิเคราะห์ข้อความลาได้")

        response_json = json.loads(gemini_response)

        created_at = get_datetime_now()

        for leave in response_json.get("leave_request", []):
            absent_date = leave.get("absent_date")
            leave_type = leave.get("leave_type")
            partial_leave = (
                leave.get("partial_leave")
                if leave.get("partial_leave") != "fullday"
                else None
            )
            content = message.content.strip()
            message_id = str(message.id)
            author_id = str(message.author.id)
            channel_id = str(message.channel.id)

            await self.leave_repository.insert_leave(
                message_id=message_id,
                author_id=author_id,
                channel_id=channel_id,
                content=content,
                leave_type=leave_type,
                partial_leave=partial_leave,
                absent_date=absent_date,
                created_at=created_at,
            )
