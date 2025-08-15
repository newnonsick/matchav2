from datetime import date
from typing import TYPE_CHECKING, Optional

from models import DailyLeaveSummary, LeaveByDateChannel, LeaveRequest

if TYPE_CHECKING:
    from db.supabase import SupabaseClient


class LeaveRepository:

    def __init__(self, supabase_client: "SupabaseClient"):
        self.supabase_client = supabase_client

    async def get_user_inleave(self, channel_id: str, target_date: date) -> list:
        client = await self.supabase_client.get_client()
        try:
            response = await client.rpc(
                "get_attendance_by_date_channel",
                {"_date": target_date.isoformat(), "_channel_id": channel_id},
            ).execute()
        except Exception as e:
            print(f"Error fetching user in leave: {e}")
            return []
        return (
            [LeaveByDateChannel(**item) for item in response.data if response.data]
            if response.data
            else []
        )

    async def get_daily_leaves(self, target_date: date) -> list[DailyLeaveSummary]:
        client = await self.supabase_client.get_client()
        response = await client.rpc(
            "get_attendance_by_date",
            {"target_date": target_date.isoformat()},
        ).execute()
        return (
            [DailyLeaveSummary(**item) for item in response.data]
            if response.data
            else []
        )

    async def insert_leave(self, leave_request: LeaveRequest) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("attendance").insert(leave_request.model_dump()).execute()

    async def get_leave_by_message_id(self, message_id: str) -> Optional[LeaveRequest]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("attendance")
            .select(
                "message_id, author_id, channel_id, content, leave_type, partial_leave, absent_date, created_at"
            )
            .eq("message_id", message_id)
            .execute()
        )
        return (
            LeaveRequest(**response.data[0])
            if response.data and len(response.data) > 0
            else None
        )

    async def delete_leave_by_message_id(self, message_id: str) -> None:
        client = await self.supabase_client.get_client()
        await client.from_("attendance").delete().eq("message_id", message_id).execute()

    async def get_leave_by_userid_and_date(
        self, user_id: str, from_date: date, to_date: date
    ) -> list[LeaveRequest]:
        client = await self.supabase_client.get_client()
        response = (
            await client.from_("attendance")
            .select(
                "absent_date, message_id, created_at, author_id, content, leave_type, partial_leave, channel_id"
            )
            .eq("author_id", user_id)
            .gte("absent_date", from_date.isoformat())
            .lte("absent_date", to_date.isoformat())
            .execute()
        )
        return [LeaveRequest(**item) for item in response.data] if response.data else []
