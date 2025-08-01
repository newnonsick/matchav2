import math
import re
from datetime import datetime
from typing import TYPE_CHECKING, Literal, Optional

import discord

from config import IGNORED_BOT_IDS, LEAVE_TYPE_MAP, PARTIAL_LEAVE_MAP
from models import (
    LeaveByDateChannel,
    LeaveRequest,
    MemberTeam,
    StandupChannel,
    StandupMessage,
    UserStandupReport,
)
from utils.datetime_utils import (
    combine_date_with_specific_time,
    combine_date_with_start_time,
    compare_date_with_today,
    convert_to_bangkok,
    get_date_now,
    get_previous_weekdays,
)

if TYPE_CHECKING:
    from repositories.standup_repository import StandupRepository
    from services.leave_service import LeaveService
    from services.member_service import MemberService
    from services.office_entry_service import OfficeEntryService


class StandupService:

    def __init__(
        self,
        standupRepository: "StandupRepository",
        memberService: "MemberService",
        leaveService: "LeaveService",
        officeEntryService: "OfficeEntryService",
    ):
        self.standupRepository = standupRepository
        self.memberService = memberService
        self.leaveService = leaveService
        self.officeEntryService = officeEntryService

    async def get_standup_channel_ids(self) -> list[int]:
        response = await self.standupRepository.get_standup_channel_ids()
        return [
            int(team["channel_id"])
            for team in response
            if "channel_id" in team and team["channel_id"]
        ]

    async def get_userid_wrote_standup(
        self, channel_id: int, from_datetime: str, to_datatime: str
    ) -> list[int]:
        response = await self.standupRepository.get_userid_wrote_standup(
            channel_id, from_datetime, to_datatime
        )
        return [
            int(message["author_id"])
            for message in response
            if "author_id" in message and message["author_id"]
        ]

    async def userid_in_standup_channel(self, channel_id: int) -> list[int]:
        response = await self.standupRepository.userid_in_standup_channel(channel_id)
        return [
            int(message["author_id"])
            for message in response
            if "author_id" in message and message["author_id"]
        ]

    async def track_standup(
        self,
        message: discord.Message,
        check_is_exist: bool = True,
        bypass_check_date: bool = False,
    ) -> Literal["today", "future", "past"]:
        if check_is_exist:
            response = await self.standupRepository.get_standup_by_message_id(
                str(message.id)
            )
            if response:
                raise ValueError(
                    f"Message with ID {message.id} already exists in the standup database."
                )

        message_content = message.content.strip()
        pattern = r"\b\d{2}/\d{2}/\d{4}\b"

        dates = re.findall(pattern, message_content)
        if not dates:
            raise ValueError(
                f"Message with ID {message.id} from {message.author.id} does not contain a valid date in the format DD/MM/YYYY."
            )

        time_status = compare_date_with_today(dates[0])
        if not bypass_check_date and time_status == "past":
            raise ValueError(
                f"Message with ID {message.id} from {message.author.id} contains a date in the past: {dates[0]}."
            )

        if message.author.id in IGNORED_BOT_IDS:
            pattern = r"(\S+)\s<@(\d+)>"
            matches = re.findall(pattern, message_content)
            if not matches:
                raise ValueError(
                    f"Message with ID {message.id} from {message.author.id} does not contain any user mentions or username."
                )
            user = matches[0]
            user_name = user[0]
            user_display_name = user[0]
            user_id = int(user[1])
        else:
            user_id = message.author.id
            user_name = message.author.name
            user_display_name = (
                message.author.display_name
                if message.author.display_name
                else user_name
            )

        message_datetime = message.created_at

        date = dates[0]
        if time_status == "future":
            timestamp = combine_date_with_start_time(date)
        else:
            timestamp = combine_date_with_specific_time(
                date, convert_to_bangkok(message_datetime).time()
            )

        standup_message = StandupMessage(
            message_id=str(message.id),
            author_id=str(user_id),
            username=user_name,
            servername=user_display_name,
            channel_id=str(message.channel.id),
            content=message_content,
            timestamp=timestamp,
        )

        # content = message_contect.replace(date, "").strip()

        await self.standupRepository.track_standup(standup_message)

        if "เข้าบริษัท" in message_content:
            await self.officeEntryService.track_office_entry(
                author_id=str(user_id),
                message_id=str(message.id),
                date=datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d"),
            )

        return time_status

    async def get_standup_embed(
        self,
        user_inleaves: list[LeaveByDateChannel],
        userid_in_standup_channel: list[int],
        userid_wrote_standup: list[int],
        channel_id: int,
        date: str,
    ) -> discord.Embed:

        users_inleave_map = {}
        for user_inleave in user_inleaves:
            users_inleave_map[int(user_inleave.author_id)] = {
                "leave_type": LEAVE_TYPE_MAP.get(
                    user_inleave.leave_type, "ไม่ระบุประเภทลา"
                ),
                "partial_leave": PARTIAL_LEAVE_MAP.get(
                    user_inleave.partial_leave or "", ""
                ),
                "content": user_inleave.content,
            }

        team_members = []
        inleave_members = []
        for user_id in userid_in_standup_channel:
            if (user_id in userid_wrote_standup) and (
                user_id in users_inleave_map.keys()
            ):
                team_members.append(
                    f"- <@{user_id}> ✅ {users_inleave_map[user_id]['leave_type']} {users_inleave_map[user_id]['partial_leave']}"
                )
                inleave_members.append(
                    f"- <@{user_id}> {users_inleave_map[user_id]['content']}"
                )
            elif user_id in userid_wrote_standup:
                team_members.append(f"- <@{user_id}> ✅")
            elif user_id in users_inleave_map.keys():
                team_members.append(
                    f"- <@{user_id}> {users_inleave_map[user_id]['leave_type']} {users_inleave_map[user_id]['partial_leave']}"
                )
                inleave_members.append(
                    f"- <@{user_id}> {users_inleave_map[user_id]['content']}"
                )
            else:
                team_members.append(f"- <@{user_id}> ❌")

        team_members_split = [
            team_members[i : i + 25] for i in range(0, len(team_members), 25)
        ]

        inleave_members_split = [
            inleave_members[i : i + 25] for i in range(0, len(inleave_members), 25)
        ]

        embed = discord.Embed(
            title=f"**รายละเอียดทีม <#{channel_id}> ประจำวันที่ {date}**",
            color=discord.Color.blue(),
        )

        for team_members in team_members_split:
            embed.add_field(
                name=f"สมาชิกทีม",
                value="\n".join(team_members) if team_members else "ไม่มีสมาชิกในทีม",
                inline=True,
            )

        if inleave_members_split:
            for inleave_members in inleave_members_split:
                embed.add_field(
                    name="สถานะการลาวันนี้",
                    value=("\n".join(inleave_members)),
                    inline=False,
                )
        else:
            embed.add_field(
                name="สถานะการลาวันนี้",
                value="ไม่มีสมาชิกที่ลาในวันนี้",
                inline=False,
            )

        embed.set_footer(
            text=f"Made With ❤️ By TN Backend Min",
        )

        return embed

    async def regis_new_standup_channel(
        self,
        channel_id: int,
        team_name: str,
        server_id: int,
        server_name: str,
        timestamp: str,
    ) -> None:
        try:
            standup_channel = StandupChannel(
                channel_id=str(channel_id),
                team_name=team_name,
                server_id=str(server_id),
                server_name=server_name,
                timestamp=timestamp,
            )
            await self.standupRepository.regis_new_standup_channel(standup_channel)
        except Exception as e:
            print(f"Error registering new standup channel {channel_id}: {e}")
            raise ValueError(f"Failed to register new standup channel: {e}")

    async def delete_standup_by_message_id(self, message_id: int) -> None:
        response: Optional[StandupMessage] = (
            await self.standupRepository.get_standup_by_message_id(str(message_id))
        )
        if response:
            await self.standupRepository.delete_standup_by_message_id(str(message_id))

    async def get_standups_by_user_and_datetime(
        self, user_id: int, from_datetime: datetime, to_datetime: datetime
    ) -> list[UserStandupReport]:
        from_datetime_str = from_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        to_datetime_str = to_datetime.strftime("%Y-%m-%dT%H:%M:%S%z")
        response: list[UserStandupReport] = (
            await self.standupRepository.get_standups_by_user_and_datetime(
                str(user_id), from_datetime_str, to_datetime_str
            )
        )
        return response

    async def get_monthly_standup_embed(
        self,
        user_standup_data: list[UserStandupReport],
        user_leave_data: list[LeaveRequest],
        month_weekdays: list[datetime],
        month: str,
    ) -> discord.Embed:
        embed = discord.Embed(
            title=f"**สรุป Stand-Up ประจำเดือน {month}**", color=discord.Color.blue()
        )

        monthly_reports: list[str] = []

        for weekday in month_weekdays:
            date_check_str = weekday.strftime("%Y-%m-%d")
            date_str = weekday.strftime("%d/%m/%Y")
            user_standup = next(
                (
                    report
                    for report in user_standup_data
                    if convert_to_bangkok(
                        datetime.fromisoformat(report.timestamp)
                    ).date()
                    == weekday.date()
                ),
                None,
            )
            user_leave = next(
                (
                    leave
                    for leave in user_leave_data
                    if leave.absent_date == date_check_str
                ),
                None,
            )

            if user_standup and user_leave:
                leave_type_display = LEAVE_TYPE_MAP.get(
                    user_leave.leave_type, "ไม่ระบุประเภท"
                )
                partial_leave_display = PARTIAL_LEAVE_MAP.get(
                    user_leave.partial_leave or "", ""
                )
                monthly_reports.append(
                    f"**{date_str}** ✅ {leave_type_display} {partial_leave_display}"
                )
            elif user_standup:
                monthly_reports.append(f"**{date_str}** ✅")
            elif user_leave:
                leave_type_display = LEAVE_TYPE_MAP.get(
                    user_leave.leave_type, "ไม่ระบุประเภท"
                )
                partial_leave_display = PARTIAL_LEAVE_MAP.get(
                    user_leave.partial_leave or "", ""
                )
                monthly_reports.append(
                    f"**{date_str}** {leave_type_display} {partial_leave_display}"
                )
            else:
                monthly_reports.append(f"**{date_str}** ❌")

        num_weekdays = len(month_weekdays)
        half_num = math.ceil(num_weekdays / 2)

        batched_reports = [
            monthly_reports[i : i + half_num]
            for i in range(0, len(monthly_reports), half_num)
        ]

        for batch in batched_reports:
            embed.add_field(
                name=f"",
                value="\n".join(batch) if batch else "ไม่มีข้อมูล",
                inline=True,
            )

        embed.set_footer(text="Made With ❤️ By TN Backend Min")
        return embed

    async def get_members_inactive_standup(self, num_days: int = 5) -> list[MemberTeam]:
        all_members = await self.memberService.get_all_standup_members()
        inactive_members: list[MemberTeam] = []

        today = get_date_now()
        previous_weekdays = get_previous_weekdays(today, num_days=num_days)
        previous_weekdays[0] = previous_weekdays[0].replace(
            hour=23, minute=59, second=59
        )

        from_datetime = previous_weekdays[-1]
        to_datetime = previous_weekdays[0]

        for member in all_members:
            member_standups = await self.get_standups_by_user_and_datetime(
                user_id=int(member.author_id),
                from_datetime=from_datetime,
                to_datetime=to_datetime,
            )

            if not member_standups:
                member_leaves = await self.leaveService.get_leave_by_userid_and_date(
                    user_id=int(member.author_id),
                    from_date=from_datetime,
                    to_date=to_datetime,
                )

                if not member_leaves:
                    inactive_members.append(member)

        return inactive_members