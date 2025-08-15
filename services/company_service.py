from typing import TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from core.custom_bot import CustomBot
    from repositories.company_repository import CompanyRepository


class CompanyService:
    def __init__(self, companyRepository: "CompanyRepository", client: "CustomBot"):
        self.companyRepository = companyRepository
        self.client = client

    async def is_holiday_date(self, date: date) -> bool:
        holiday = await self.companyRepository.get_holiday_date_by_date(date)
        return holiday is not None
