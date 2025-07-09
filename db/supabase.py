from supabase import AsyncClient, acreate_client


class SupabaseClient:

    def __init__(self, SUPABASE_URL: str, SUPABASE_KEY: str):
        self.SUPABASE_URL = SUPABASE_URL
        self.SUPABASE_KEY = SUPABASE_KEY
        self.supabase_client = None

    async def connect(self) -> AsyncClient:
        if not self.supabase_client:
            self.supabase_client = await acreate_client(
                self.SUPABASE_URL, self.SUPABASE_KEY
            )
        return self.supabase_client

    async def get_client(self) -> AsyncClient:
        if not self.supabase_client:
            raise ValueError(
                "Supabase client has not been created. Call connect() first."
            )
        return self.supabase_client
