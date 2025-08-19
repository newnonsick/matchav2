from datetime import date
from typing import TYPE_CHECKING, Optional

from models import DailyLeaveSummary, LeaveByDateChannel, LeaveRequest

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class LeaveRepository:

    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def get_user_inleave(self, channel_id: str, target_date: date) -> list:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT a.author_id, a.leave_type, a.partial_leave, a.content
                FROM attendance a
                JOIN member_team m ON a.author_id = m.author_id
                WHERE a.absent_date = $1 AND m.channel_id = $2
                ORDER BY m.server_name asc;
                """,
                target_date,
                channel_id,
            )
            return [LeaveByDateChannel(**dict(row)) for row in rows] if rows else []
        except Exception as e:
            print(f"Error fetching user in leave: {e}")
            return []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_daily_leaves(self, target_date: date) -> list[DailyLeaveSummary]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT
                    a.author_id,
                    a.leave_type,
                    a.partial_leave,
                    t.team_name
                FROM public.attendance a
                JOIN public.member_team mt on a.author_id = mt.author_id 
                JOIN public.team t on mt.channel_id = t.channel_id
                WHERE a.absent_date = $1
                ORDER BY t.team_name asc, mt.server_name asc;
                """,
                target_date,
            )
            return [DailyLeaveSummary(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def insert_leave(self, leave_request: LeaveRequest) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO attendance (message_id, author_id, channel_id, content, leave_type, partial_leave, absent_date, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                leave_request.message_id,
                leave_request.author_id,
                leave_request.channel_id,
                leave_request.content,
                leave_request.leave_type,
                leave_request.partial_leave,
                leave_request.absent_date,
                leave_request.created_at,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_leave_by_message_id(self, message_id: str) -> Optional[LeaveRequest]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                """
                SELECT message_id, author_id, channel_id, content, leave_type, partial_leave, absent_date, created_at
                FROM attendance
                WHERE message_id = $1
                """,
                message_id,
            )
            return LeaveRequest(**dict(row)) if row else None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def delete_leave_by_message_id(self, message_id: str) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                "DELETE FROM attendance WHERE message_id = $1", message_id
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_leave_by_userid_and_date(
        self, user_id: str, from_date: date, to_date: date
    ) -> list[LeaveRequest]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT absent_date, message_id, created_at, author_id, content, leave_type, partial_leave, channel_id
                FROM attendance
                WHERE author_id = $1 AND absent_date >= $2 AND absent_date <= $3
                ORDER BY absent_date ASC
                """,
                user_id,
                from_date,
                to_date,
            )
            return [LeaveRequest(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
