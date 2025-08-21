import asyncpg


class AsyncpgClient:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Create a new pool if not exists."""
        if not self.pool or self.pool._closed:
            self.pool = await asyncpg.create_pool(
                self.dsn,
                max_inactive_connection_lifetime=0,
            )

    async def get_connection(self) -> asyncpg.Connection:
        """Acquire a connection, reconnect if pool is closed."""
        if not self.pool or self.pool._closed:
            await self.connect()
        try:
            if not self.pool:
                raise ConnectionError("Connection pool is not initialized.")
            return await self.pool.acquire()
        except (asyncpg.PostgresError, ConnectionError):
            await self.connect()
            if not self.pool:
                raise ConnectionError("Failed to acquire a connection from the pool.")
            return await self.pool.acquire()

    async def release_connection(self, conn: asyncpg.Connection) -> None:
        if self.pool and not self.pool._closed:
            await self.pool.release(conn)

    async def close(self) -> None:
        if self.pool and not self.pool._closed:
            await self.pool.close()