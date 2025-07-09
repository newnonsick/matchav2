from supabase import AsyncClient

from db.supabase import SupabaseClient


class LeaveRepository:

    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client: SupabaseClient = supabase_client

    async def get_user_inleave(self, channel_id: int, date: str) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = await client.rpc(
            "get_attendance_by_date_channel",
            {"_date": date, "_channel_id": str(channel_id)},
        ).execute()
        return response.data if response.data else []

    async def get_daily_leaves(self, date: str) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = await client.rpc(
            "get_attendance_by_date",
            {"target_date": date},
        ).execute()
        return response.data if response.data else []

    async def insert_leave(
        self,
        message_id: str,
        author_id: str,
        channel_id: str,
        content: str,
        leave_type: str,
        partial_leave: str | None,
        absent_date: str,
        created_at: str,
    ) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("attendance").insert(
            {
                "message_id": message_id,
                "author_id": author_id,
                "channel_id": channel_id,
                "content": content,
                "leave_type": leave_type,
                "partial_leave": partial_leave,
                "absent_date": absent_date,
                "created_at": created_at,
            }
        ).execute()

    async def get_leave_by_message_id(self, message_id: str) -> list:
        client: AsyncClient = await self.supabase_client.get_client()
        response = (
            await client.from_("attendance")
            .select("content, leave_type, partial_leave, content")
            .eq("message_id", message_id)
            .execute()
        )
        return response.data if response.data else []
    
    async def delete_leave_by_message_id(self, message_id: str) -> None:
        client: AsyncClient = await self.supabase_client.get_client()
        await client.from_("attendance").delete().eq("message_id", message_id).execute()
