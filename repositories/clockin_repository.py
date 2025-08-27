from datetime import date, datetime
from typing import TYPE_CHECKING

from models import ClockinLog

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class ClockinRepository:
    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def create_clockin_log(self, author_id: str, clockin_time: datetime) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO clockin_log (author_id, clock_in_time)
                VALUES ($1, $2)
                """,
                author_id,
                clockin_time,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_clockin_by_author_and_date(self, author_id: str, target_date: date) -> ClockinLog | None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                """
                SELECT id, author_id, clock_in_time
                FROM clockin_log
                WHERE author_id = $1 AND DATE(clock_in_time) = $2
                """,
                author_id,
                target_date,
            )
            if row:
                return ClockinLog(
                    id=row["id"],
                    author_id=row["author_id"],
                    clock_in_time=row["clock_in_time"],
                )
            return None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
