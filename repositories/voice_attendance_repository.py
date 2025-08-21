from datetime import date, datetime
from typing import TYPE_CHECKING
from typing_extensions import Literal

from models import DailyVoiceAttendance

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class VoiceAttendanceRepository:
    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def get_daily_attendance_summary_by_channel_id_and_date(
        self, channel_id: int, date: date
    ) -> list[DailyVoiceAttendance]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                WITH joined AS (
                    SELECT
                        author_id,
                        date,
                        event_type,
                        event_time AT TIME ZONE 'Asia/Bangkok' AS local_time,
                        LEAD(event_time) OVER (PARTITION BY author_id, date ORDER BY event_time) AS next_time_utc,
                        LEAD(event_type) OVER (PARTITION BY author_id, date ORDER BY event_time) AS next_type
                    FROM attendance_activity
                    WHERE date = $2::date
                ),
                intervals AS (
                    SELECT
                        author_id,
                        date,
                        local_time AS join_time,
                        CASE
                            WHEN next_type = 'leave' THEN (next_time_utc AT TIME ZONE 'Asia/Bangkok')
                            WHEN next_time_utc IS NULL THEN (now() AT TIME ZONE 'Asia/Bangkok')
                            ELSE NULL
                        END AS leave_time
                    FROM joined
                    WHERE event_type = 'join'
                    AND (next_type = 'leave' OR next_time_utc IS NULL)
                ),
                users AS (
                    SELECT author_id, server_name
                    FROM member_team
                    WHERE channel_id = $1
                )
                SELECT
                    u.author_id,
                    u.server_name,
                    CASE
                        WHEN EXTRACT(DOW FROM $2::date) IN (0,6) THEN 'weekend'
                        WHEN EXISTS (SELECT 1 FROM company_holidays h WHERE h.holiday_date = $2::date) THEN 'holiday'
                        WHEN EXISTS (
                            SELECT 1 FROM attendance a
                            WHERE a.author_id = u.author_id
                            AND a.absent_date = $2::date
                            AND (a.partial_leave = 'morning' OR a.partial_leave IS NULL)
                        ) THEN 'leave'
                        WHEN EXISTS (
                            SELECT 1 FROM intervals iv
                            WHERE iv.author_id = u.author_id
                            AND iv.date = $2::date
                            AND iv.join_time >= ($2::date + interval '8 hours')
                            AND iv.join_time <=  ($2::date + interval '9 hours')
                            AND iv.leave_time > ($2::date + interval '9 hours')
                        ) THEN 'on_time'
                        WHEN EXISTS (
                            SELECT 1 FROM intervals iv
                            WHERE iv.author_id = u.author_id
                            AND iv.date = $2::date
                            AND iv.join_time > ($2::date + interval '9 hours')
                            AND iv.join_time <  ($2::date + interval '9 hours 30 minutes')
                        ) THEN 'late'
                        ELSE 'absent'
                    END AS status
                FROM users u
                ORDER BY status DESC, u.server_name;
                """,
                str(channel_id),
                date,
            )
            return [DailyVoiceAttendance(**row) for row in rows]
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

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

    async def get_lested_event_type_by_author_id(
        self, author_id: int
    ) -> Literal["join", "leave"] | None:
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
            return row["event_type"] if row else None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
