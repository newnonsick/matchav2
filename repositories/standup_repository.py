from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from typing_extensions import Literal

from models import StandupChannel, StandupMessage, StandupTask, UserStandupReport

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class StandupRepository:

    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def get_task_by_id(
        self, task_id: UUID) -> Optional[StandupTask]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                """
                SELECT id, message_id, author_id, task, status
                FROM tasks
                WHERE id = $1
                """,
                str(task_id),
            )
            return StandupTask(**dict(row)) if row else None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def update_task_status(
        self, task_id: UUID, status: Literal["todo", "in_progress", "done"]
    ) -> None:
        if status not in ["todo", "in_progress", "done"]:
            raise ValueError(f"Invalid task status: {status}")

        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                UPDATE tasks SET status = $1 WHERE id = $2
                """,
                status,
                task_id,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_standup_tasks_by_user_and_date(
        self, author_id: str, from_date: date, to_date: date) -> list[StandupTask]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT t.id, t.message_id, t.author_id, t.task , t.status
                FROM tasks t
                JOIN message m ON t.message_id = m.message_id AND t.author_id = m.author_id
                WHERE t.author_id = $1 AND m.message_date >= $2 AND m.message_date <= $3
                """,
                author_id,
                from_date,
                to_date,
            )
            return [StandupTask(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def insert_standup_tasks(
        self, message_id: str, author_id: str, tasks: list[str]) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.executemany(
                """
                INSERT INTO tasks (message_id, author_id, task)
                VALUES ($1, $2, $3)
                """,
                [(message_id, author_id, task.strip()) for task in tasks],
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_standup_channel_ids(self) -> list:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                "SELECT channel_id FROM team ORDER BY team_name ASC"
            )
            return [dict(row) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_userid_wrote_standup_by_date(
        self, channel_id: int, from_date: date, to_data: date
    ) -> list:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT author_id FROM message
                WHERE channel_id = $1 AND message_date >= $2 AND message_date <= $3
                """,
                str(channel_id),
                from_date,
                to_data,
            )
            return [dict(row) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def userid_in_standup_channel(self, channel_id: int) -> list:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                "SELECT author_id FROM member_team WHERE channel_id = $1 ORDER BY server_name ASC",
                str(channel_id),
            )
            return [dict(row) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_standup_by_message_id(
        self, message_id: str
    ) -> Optional[StandupMessage]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                """
                SELECT message_id, author_id, username, servername, channel_id, content, timestamp, last_updated_at, message_date
                FROM message
                WHERE message_id = $1
                """,
                message_id,
            )
            return StandupMessage(**dict(row)) if row else None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def track_standup(self, standup_message: StandupMessage) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO message (message_id, author_id, username, servername, channel_id, content, timestamp, last_updated_at, message_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (message_id, author_id) DO UPDATE
                SET username = EXCLUDED.username, servername = EXCLUDED.servername, content = EXCLUDED.content, timestamp = EXCLUDED.timestamp, last_updated_at = EXCLUDED.last_updated_at, message_date = EXCLUDED.message_date
                """,
                standup_message.message_id,
                standup_message.author_id,
                standup_message.username,
                standup_message.servername,
                standup_message.channel_id,
                standup_message.content,
                standup_message.timestamp,
                standup_message.last_updated_at,
                standup_message.message_date,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def regis_new_standup_channel(self, standup_channel: StandupChannel) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO team (channel_id, team_name, server_id, server_name, timestamp)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (channel_id) DO NOTHING
                """,
                standup_channel.channel_id,
                standup_channel.team_name,
                standup_channel.server_id,
                standup_channel.server_name,
                standup_channel.timestamp,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def delete_standup_by_message_id(self, message_id: int) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                "DELETE FROM message WHERE message_id = $1", str(message_id)
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_standups_by_user_and_date(
        self, user_id: str, from_date: date, to_date: date
    ) -> list[UserStandupReport]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT content, message_date, timestamp, last_updated_at FROM message
                WHERE author_id = $1 AND message_date >= $2 AND message_date <= $3
                ORDER BY timestamp ASC
                """,
                user_id,
                from_date,
                to_date,
            )
            return [UserStandupReport(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
