from discord.ext import commands

from config import (
    GEMINI_API_KEY,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USERNAME,
    SUPABASE_KEY,
    SUPABASE_URL,
)
from db.supabase import SupabaseClient
from repositories.leave_repository import LeaveRepository
from repositories.member_repository import MemberRepository
from repositories.standup_repository import StandupRepository
from services.email_service import EmailService
from services.gemini_service import GeminiService
from services.leave_service import LeaveService
from services.member_service import MemberService
from services.standup_report_generator import StandupReportGenerator
from services.standup_service import StandupService


class CustomBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db: SupabaseClient = SupabaseClient(
            SUPABASE_URL=SUPABASE_URL, SUPABASE_KEY=SUPABASE_KEY
        )
        self.member_repository = MemberRepository(self.db)
        self.member_service = MemberService(self.member_repository)
        self.leave_repository = LeaveRepository(self.db)
        self.gemini_service = GeminiService(GEMINI_API_KEY)
        self.leave_service = LeaveService(self.leave_repository, self.gemini_service)
        self.standup_repository = StandupRepository(self.db)
        self.standup_service = StandupService(
            self.standup_repository, self.member_service, self.leave_service
        )
        self.standup_report_generator = StandupReportGenerator()
        self.email_service = EmailService(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            smtp_username=SMTP_USERNAME,
            smtp_password=SMTP_PASSWORD,
        )

    async def close(self):
        # Custom cleanup logic can be added here if needed
        print("Closing the bot and cleaning up resources.")
        await super().close()
