import asyncpg


class AsyncpgClient:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self) -> None:
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                self.dsn,
                max_inactive_connection_lifetime=0,
            )

    async def get_connection(self) -> asyncpg.Connection:
        if not self.pool:
            raise ValueError(
                "Connection pool has not been created. Call connect() first."
            )
        return await self.pool.acquire()

    async def release_connection(self, conn) -> None:
        if self.pool:
            await self.pool.release(conn)

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
