from datetime import date
from typing import TYPE_CHECKING

from models import DailyOfficeEntrySummary, OfficeEntry

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class OfficeEntryRepository:
    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def insert_office_entry(self, entry: OfficeEntry):
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO office_entries (author_id, message_id, date, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (author_id, date) DO NOTHING
                """,
                entry.author_id,
                entry.message_id,
                entry.date,
                entry.created_at,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_daily_office_entries(
        self, target_date: date
    ) -> list[DailyOfficeEntrySummary]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT
                    oe.author_id,
                    mt.server_name,
                    t.team_name
                FROM public.office_entries oe
                JOIN public.member_team mt on oe.author_id = mt.author_id
                JOIN public.team t on mt.channel_id = t.channel_id
                WHERE oe.date = $1
                ORDER BY t.team_name asc, mt.server_name asc;
                """,
                target_date,
            )
            return (
                [DailyOfficeEntrySummary(**dict(row)) for row in rows] if rows else []
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_office_entry_by_author_id_and_date(
        self, author_id: str, target_date: date
    ) -> OfficeEntry | None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                """
                SELECT author_id, message_id, date, created_at
                FROM office_entries
                WHERE author_id = $1 AND date = $2
                LIMIT 1
                """,
                author_id,
                target_date,
            )
            return OfficeEntry(**dict(row)) if row else None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
