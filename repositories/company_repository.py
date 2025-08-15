from datetime import date
from typing import TYPE_CHECKING, Optional

from models import CompanyHoliday

if TYPE_CHECKING:
    from db.supabase import SupabaseClient


class CompanyRepository:
    def __init__(self, supabase_client: "SupabaseClient"):
        self.supabase_client = supabase_client

    async def get_holiday_date_by_date(self, target_date: date) -> Optional[CompanyHoliday]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("company_holidays")
            .select("holiday_date, description")
            .eq("holiday_date", target_date.isoformat())
            .execute()
        )
        if response.data:
            return CompanyHoliday(**response.data[0])
        return None
