from typing import TYPE_CHECKING, Optional

from models import MemberTeam, StandupMember, Team

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class MemberRepository:

    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def get_all_standup_members(self) -> list[MemberTeam]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch("SELECT author_id, server_name FROM member_team")
            return [MemberTeam(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_standup_members_by_channelid(
        self, channel_id: str
    ) -> list[MemberTeam]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                "SELECT author_id, server_name FROM member_team WHERE channel_id = $1",
                channel_id,
            )
            return [MemberTeam(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def add_member_to_standup_channel(
        self, standup_member: StandupMember
    ) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO member_team (channel_id, author_id, server_name, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (channel_id, author_id) DO UPDATE
                SET server_name = EXCLUDED.server_name, created_at = EXCLUDED.created_at
                """,
                standup_member.channel_id,
                standup_member.author_id,
                standup_member.server_name,
                standup_member.created_at,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def is_user_added_to_standup_channel(
        self, channel_id: int, user_id: int
    ) -> bool:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                "SELECT author_id FROM member_team WHERE channel_id = $1 AND author_id = $2",
                str(channel_id),
                str(user_id),
            )
            return bool(row)
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def remove_member_from_standup_channel(
        self, channel_id: int, user_id: int
    ) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                "DELETE FROM member_team WHERE channel_id = $1 AND author_id = $2",
                str(channel_id),
                str(user_id),
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def remove_member_from_all_standup_channels(self, user_id: str) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute("DELETE FROM member_team WHERE author_id = $1", user_id)
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_user_role(self, user_id: str) -> Optional[str]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                "SELECT role FROM member_team WHERE author_id = $1 LIMIT 1", user_id
            )
            return row["role"] if row else None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def update_user_role(self, user_id: str, role: str) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                "UPDATE member_team SET role = $1 WHERE author_id = $2", role, user_id
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_standup_channels_by_user_id(self, user_id: str) -> list[Team]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT t.channel_id, t.server_id, t.server_name, t.team_name
                FROM member_team mt
                JOIN team t ON mt.channel_id = t.channel_id
                WHERE mt.author_id = $1
                """,
                user_id,
            )
            return [Team(**dict(row)) for row in rows] if rows else []
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def is_user_exists(self, user_id: str) -> bool:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                "SELECT author_id FROM member_team WHERE author_id = $1 LIMIT 1",
                user_id,
            )
            return bool(row)
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def update_member_display_name(
        self, user_id: str, new_display_name: str
    ) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                "UPDATE member_team SET server_name = $1 WHERE author_id = $2",
                new_display_name,
                user_id,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
