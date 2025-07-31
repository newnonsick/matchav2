from typing import TYPE_CHECKING, Optional

import discord

from datacache import DataCache
from models import DailyOfficeEntrySummary, OfficeEntry
from utils.datetime_utils import get_date_now, get_datetime_now

if TYPE_CHECKING:
    from repositories.member_repository import MemberRepository
    from repositories.office_entry_repository import OfficeEntryRepository


class OfficeEntryService:
    def __init__(
        self,
        office_entry_repository: "OfficeEntryRepository",
        member_repository: "MemberRepository",
    ):
        self.office_entry_repository = office_entry_repository
        self.member_repository = member_repository

    async def track_office_entry(
        self, author_id: str, message_id: str, date: str
    ) -> None:
        existing_entry = (
            await self.office_entry_repository.get_office_entry_by_author_id_and_date(
                author_id, date
            )
        )
        if existing_entry:
            return

        entry = OfficeEntry(
            author_id=author_id,
            message_id=message_id,
            date=date,
            created_at=get_datetime_now(),
        )
        await self.office_entry_repository.insert_office_entry(entry)

    async def get_daily_office_entries(
        self, date: str
    ) -> list[DailyOfficeEntrySummary]:
        return await self.office_entry_repository.get_daily_office_entries(date)

    async def get_daily_office_entries_embed(
        self, entries: list[DailyOfficeEntrySummary], date: str
    ) -> discord.Embed:
        embed = discord.Embed(
            title=f"**รายงานการเข้าบริษัท ประจำวันที่ {date}**",
            color=discord.Color.from_rgb(102, 204, 255),
        )

        if not entries:
            embed.description = "วันนี้ยังไม่มีใครเข้าบริษัท"
            return embed

        team_entries: dict[str, list[str]] = {}
        for entry in entries:
            if entry.team_name not in team_entries:
                team_entries[entry.team_name] = []
            team_entries[entry.team_name].append(
                f"- <@{entry.author_id}>"  # ({entry.server_name})
            )

        sorted_team_names = sorted(team_entries.keys())

        for team_name in sorted_team_names:
            members = team_entries[team_name]
            embed.add_field(
                name=f"👶 {team_name}" if "trainee" in team_name else f"🏢 {team_name}",
                value="\n".join(members),
                inline=False,
            )

        total_members = len(set(entry.author_id for entry in entries))

        embed.set_footer(text=f"รวม {total_members} คน เข้าบริษัทวันนี้")
        return embed

    async def update_daily_office_entry_summary(
        self, date: Optional[str] = None
    ) -> None:

        if not date:
            date = get_date_now()

        message = DataCache.daily_office_entry_summary.get(date)
        if not message:
            return

        entries = await self.get_daily_office_entries(date)
        embed = await self.get_daily_office_entries_embed(entries, date)

        await message.edit(embed=embed)
