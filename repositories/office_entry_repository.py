from typing import TYPE_CHECKING

from models import DailyOfficeEntrySummary, OfficeEntry

if TYPE_CHECKING:
    from db.supabase import SupabaseClient


class OfficeEntryRepository:
    def __init__(self, supabase_client: "SupabaseClient"):
        self.supabase_client = supabase_client

    async def insert_office_entry(self, entry: OfficeEntry):
        client = await self.supabase_client.get_client()
        await client.from_("office_entries").insert(entry.model_dump()).execute()

    async def get_daily_office_entries(
        self, date: str
    ) -> list[DailyOfficeEntrySummary]:
        client = await self.supabase_client.get_client()
        response = await client.rpc(
            "get_daily_office_entries",
            {"target_date": date},
        ).execute()
        return (
            [DailyOfficeEntrySummary(**item) for item in response.data]
            if response.data
            else []
        )

    async def get_office_entry_by_author_id_and_date(
        self, author_id: str, date: str
    ) -> OfficeEntry | None:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("office_entries")
            .select("author_id, message_id, date, created_at")
            .eq("author_id", author_id)
            .eq("date", date)
            .limit(1)
            .execute()
        )
        if response.data:
            return OfficeEntry(**response.data[0])
        return None
