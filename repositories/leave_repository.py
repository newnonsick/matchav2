from typing import Optional

from supabase import AsyncClient

from db.supabase import SupabaseClient
from models import DailyLeaveSummary, LeaveByDateChannel, LeaveRequest


class LeaveRepository:

    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client: SupabaseClient = supabase_client

    async def get_user_inleave(self, channel_id: int, date: str) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = await client.rpc(
            "get_attendance_by_date_channel",
            {"_date": date, "_channel_id": str(channel_id)},
        ).execute()
        return (
            [LeaveByDateChannel(**item) for item in response.data if response.data]
            if response.data
            else []
        )

    async def get_daily_leaves(self, date: str) -> list[DailyLeaveSummary]:
        client: AsyncClient = await self.supabase_client.get_client()
        response = await client.rpc(
            "get_attendance_by_date",
            {"target_date": date},
        ).execute()
        return (
            [DailyLeaveSummary(**item) for item in response.data]
            if response.data
            else []
        )

    async def insert_leave(self, leave_request: LeaveRequest) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("attendance").insert(leave_request.model_dump()).execute()

    async def get_leave_by_message_id(self, message_id: str) -> Optional[LeaveRequest]:
        client: AsyncClient = await self.supabase_client.get_client()
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
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("attendance").delete().eq("message_id", message_id).execute()

    async def get_leave_by_userid_and_datetime(
        self, user_id: str, from_datetime: str, to_datetime: str
    ) -> list[LeaveRequest]:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("attendance")
            .select(
                "absent_date, message_id, created_at, author_id, content, leave_type, partial_leave, channel_id"
            )
            .eq("author_id", user_id)
            .gte("created_at", from_datetime)
            .lte("created_at", to_datetime)
            .execute()
        )
        return [LeaveRequest(**item) for item in response.data] if response.data else []
