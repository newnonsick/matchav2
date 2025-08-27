from datetime import date
from typing import TYPE_CHECKING, Optional

from models import BotPanel

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class BotPanelRepository:
    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def get_bot_panel(self) -> Optional[BotPanel]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                "SELECT message_id, channel_id FROM bot_panel WHERE id = TRUE"
            )
            if row:
                return BotPanel(
                    message_id=row["message_id"], channel_id=row["channel_id"]
                )
            return None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def delete_bot_panel(self) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute("DELETE FROM bot_panel WHERE id = TRUE")
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def insert_bot_panel(self, message_id: int, channel_id: int) -> None:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            await conn.execute(
                """
                INSERT INTO bot_panel (id, message_id, channel_id, created_at)
                VALUES (TRUE, $1, $2, NOW())
                ON CONFLICT (id) DO UPDATE SET message_id = EXCLUDED.message_id, channel_id = EXCLUDED.channel_id, created_at = EXCLUDED.created_at
                """,
                message_id,
                channel_id,
            )
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
