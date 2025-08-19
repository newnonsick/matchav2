from datetime import datetime
from typing import TYPE_CHECKING, Optional

from models import StandupChannel, StandupMessage, UserStandupReport

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class StandupRepository:

    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def get_standup_channel_ids(self) -> list:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch("SELECT channel_id FROM team")
            return [dict(row) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_userid_wrote_standup(
        self, channel_id: int, from_datetime: datetime, to_datatime: datetime
    ) -> list:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT author_id FROM message
                WHERE channel_id = $1 AND timestamp >= $2 AND timestamp <= $3
                """,
                str(channel_id),
                from_datetime,
                to_datatime,
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
                SELECT message_id, author_id, username, servername, channel_id, content, timestamp
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
                INSERT INTO message (message_id, author_id, username, servername, channel_id, content, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (message_id, author_id) DO UPDATE
                SET username = EXCLUDED.username, servername = EXCLUDED.servername, content = EXCLUDED.content, timestamp = EXCLUDED.timestamp
                """,
                standup_message.message_id,
                standup_message.author_id,
                standup_message.username,
                standup_message.servername,
                standup_message.channel_id,
                standup_message.content,
                standup_message.timestamp,
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

    async def get_standups_by_user_and_datetime(
        self, user_id: str, from_datetime: datetime, to_datetime: datetime
    ) -> list[UserStandupReport]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT content, timestamp FROM message
                WHERE author_id = $1 AND timestamp >= $2 AND timestamp <= $3
                ORDER BY timestamp ASC
                """,
                user_id,
                from_datetime,
                to_datetime,
            )
            return [UserStandupReport(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
