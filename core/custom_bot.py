from discord.ext import commands

from config import (
    DATABASE_URL,
    GEMINI_API_KEY,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USERNAME,
)
from db.asyncpg_client import AsyncpgClient
from repositories.company_repository import CompanyRepository
from repositories.leave_repository import LeaveRepository
from repositories.member_repository import MemberRepository
from repositories.office_entry_repository import OfficeEntryRepository
from repositories.standup_repository import StandupRepository
from repositories.voice_repository import VoiceRepository
from services.company_service import CompanyService
from services.email_service import EmailService
from services.gemini_service import GeminiService
from services.leave_service import LeaveService
from services.member_service import MemberService
from services.office_entry_service import OfficeEntryService
from services.standup_report_generator import StandupReportGenerator
from services.standup_service import StandupService
from services.voice_service import VoiceService


class CustomBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = AsyncpgClient(dsn=DATABASE_URL)
        self.member_repository = MemberRepository(self.db)
        self.member_service = MemberService(self.member_repository, self)
        self.leave_repository = LeaveRepository(self.db)
        self.gemini_service = GeminiService(GEMINI_API_KEY)
        self.office_entry_repository = OfficeEntryRepository(self.db)
        self.office_entry_service = OfficeEntryService(
            self.office_entry_repository, self.member_repository
        )
        self.leave_service = LeaveService(
            self.leave_repository, self.gemini_service, self
        )
        self.standup_repository = StandupRepository(self.db)
        self.standup_service = StandupService(
            self.standup_repository,
            self.member_service,
            self.leave_service,
            self.office_entry_service,
        )
        self.standup_report_generator = StandupReportGenerator()
        self.email_service = EmailService(
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            smtp_username=SMTP_USERNAME,
            smtp_password=SMTP_PASSWORD,
        )
        self.company_repository = CompanyRepository(self.db)
        self.company_service = CompanyService(self.company_repository, self)
        self.voice_repository = VoiceRepository(self.db)
        self.voice_service = VoiceService(self.voice_repository, self)

    async def close(self):
        print("Closing the bot and cleaning up resources.")
        if self.db.pool:
            await self.db.close()
        await super().close()
