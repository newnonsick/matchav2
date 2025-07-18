import re
from typing import Optional

import discord

from config import IGNORED_BOT_IDS, LEAVE_TYPE_MAP, PARTIAL_LEAVE_MAP
from models import (
    LeaveByDateChannel,
    StandupChannel,
    StandupMember,
    StandupMessage,
    UserStandupReport,
)
from repositories.standup_repository import StandupRepository
from utils.datetime_utils import combine_date_with_current_time


class StandupService:

    def __init__(self, standupRepository: StandupRepository):
        self.standupRepository = standupRepository

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

    async def track_standup(self, message: discord.Message, check: bool = True) -> None:
        if check:
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

        date = dates[0]
        timestamp = combine_date_with_current_time(date)

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

    async def is_user_added_to_standup_channel(
        self, channel_id: int, user_id: int
    ) -> bool:
        response = await self.standupRepository.is_user_added_to_standup_channel(
            channel_id=channel_id, user_id=user_id
        )
        return response


    async def add_member_to_standup_channel(
        self, channel_id: int, user_id: int, user_name: str, created_at: str
    ) -> None:
        if await self.is_user_added_to_standup_channel(channel_id, user_id):
            raise ValueError(
                f"User <@{user_id}> is already added to standup channel <#{channel_id}>"
            )

        standup_member = StandupMember(
            channel_id=str(channel_id),
            author_id=str(user_id),
            server_name=user_name,
            created_at=created_at,
        )

        await self.standupRepository.add_member_to_standup_channel(standup_member)

    async def remove_member_from_standup_channel(
        self, channel_id: int, user_id: int
    ) -> None:
        if not await self.is_user_added_to_standup_channel(channel_id, user_id):
            raise ValueError(
                f"User <@{user_id}> is not in standup channel <#{channel_id}>"
            )

        await self.standupRepository.remove_member_from_standup_channel(
            channel_id=channel_id, user_id=user_id
        )

    async def delete_standup_by_message_id(self, message_id: int) -> None:
        response: Optional[StandupMessage] = (
            await self.standupRepository.get_standup_by_message_id(str(message_id))
        )
        if response:
            await self.standupRepository.delete_standup_by_message_id(str(message_id))

    async def get_standups_by_user_and_month(
        self, user_id: int, from_datetime: str, to_datetime: str
    ) -> list[UserStandupReport]:
        response: list[UserStandupReport] = (
            await self.standupRepository.get_standups_by_user_and_month(
                str(user_id), from_datetime, to_datetime
            )
        )
        return response
