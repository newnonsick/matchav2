from datetime import date, datetime
from typing import TYPE_CHECKING
from typing_extensions import Literal

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class VoiceRepository:
    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def insert_voice_log(
        self, author_id: str, event_time: datetime, event_type: str, date: date
    ):
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO attendance_activity (author_id, event_time, event_type, date)
                VALUES ($1, $2, $3, $4)
                """,
                author_id,
                event_time,
                event_type,
                date,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_lested_event_type_by_author_id(self, author_id: int) -> Literal["join", "leave"]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                """
                SELECT event_type FROM attendance_activity
                WHERE author_id = $1
                ORDER BY event_time DESC
                LIMIT 1
                """,
                str(author_id),
            )
            return row["event_type"] if row else "leave"
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
