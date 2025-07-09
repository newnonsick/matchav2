import asyncio
import json

import discord

from config import LEAVE_TYPE_MAP, PARTIAL_LEAVE_MAP
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

        if not team_leaves:
            embed.description = "ไม่มีพนักงานลาประจำวันนี้"
            return embed

        for team_name, members in team_leaves.items():
            embed.add_field(
                name=f"👶 {team_name}" if "trainee" in team_name else f"🏢 {team_name}",
                value="\n".join(
                    f"<@{member['author_id']}> - {LEAVE_TYPE_MAP.get(member['leave_type'])} {PARTIAL_LEAVE_MAP.get(member['partial_leave'], '')}"
                    for member in members
                ),
                inline=False,
            )

        return embed

    async def track_leave(self, message: discord.Message) -> list:
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
            partial_leave = leave.get("partial_leave")
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

        return response_json.get("leave_request", [])

    async def send_leave_confirmation(
        self, leave_request: list, message: discord.Message
    ) -> None:
        if not leave_request:
            return

        embed_color = discord.Color.from_rgb(52, 152, 219)

        embed = discord.Embed(
            title="การบันทึกการลาเสร็จสมบูรณ์",
            description="สรุปรายละเอียดการลาของคุณ:",
            color=embed_color,
        )

        for leave in leave_request:
            leave_type_display = LEAVE_TYPE_MAP.get(leave["leave_type"], "ไม่ระบุประเภท")
            partial_leave_display = PARTIAL_LEAVE_MAP.get(leave["partial_leave"], "")

            embed.add_field(
                name=f"🗓️ วันที่: {leave['absent_date']}",
                value=f"**ประเภท:** {leave_type_display} {partial_leave_display}",
                inline=False,
            )

        embed.add_field(
            name="\n📝 รายละเอียดการลา:",
            value=f"```\n{message.content}\n```",
            inline=False,
        )

        embed.set_footer(
            text="หากมีปัญหาหรือข้อสงสัย โปรดติดต่อฝ่ายทรัพยากรบุคคล | ขอให้มีความสุขกับการลา!",
        )

        await message.author.send(embed=embed)

    async def send_leave_deletion_notification(self, message: discord.Message) -> None:
        embed_color = discord.Color.from_rgb(231, 76, 60)

        embed = discord.Embed(
            title="การลาถูกลบ",
            description="ข้อความการลาได้ถูกลบออกจากระบบ",
            color=embed_color,
        )

        embed.add_field(
            name="\n📝 รายละเอียดการลา:",
            value=f"```\n{message.content}\n```",
            inline=False,
        )

        embed.set_footer(text="หากมีปัญหาหรือข้อสงสัย โปรดติดต่อฝ่ายทรัพยากรบุคคล")

        await message.author.send(embed=embed)

    async def delete_leave_by_message_id(self, message_id: int) -> None:
        response = await self.leave_repository.get_leave_by_message_id(str(message_id))
        if response:
            await self.leave_repository.delete_leave_by_message_id(str(message_id))

    async def send_edit_leave_comfirmation(
        self, leave_request: list, message: discord.Message
    ) -> None:
        if not leave_request:
            return

        embed_color = discord.Color.from_rgb(52, 152, 219)

        embed = discord.Embed(
            title="การแก้ไขการลาเสร็จสมบูรณ์",
            description="สรุปรายละเอียดการลาที่ได้รับการแก้ไข:",
            color=embed_color,
        )

        for leave in leave_request:
            leave_type_display = LEAVE_TYPE_MAP.get(leave["leave_type"], "ไม่ระบุประเภท")
            partial_leave_display = PARTIAL_LEAVE_MAP.get(leave["partial_leave"], "")

            embed.add_field(
                name=f"🗓️ วันที่: {leave['absent_date']}",
                value=f"**ประเภท:** {leave_type_display} {partial_leave_display}",
                inline=False,
            )

        embed.add_field(
            name="\n📝 รายละเอียดการลา:",
            value=f"```\n{message.content}\n```",
            inline=False,
        )

        embed.set_footer(
            text="หากมีปัญหาหรือข้อสงสัย โปรดติดต่อฝ่ายทรัพยากรบุคคล | ขอให้มีความสุขกับการลา!",
        )

        await message.author.send(embed=embed)
