from typing import TYPE_CHECKING
from datetime import date, datetime

from models import CompanyHoliday


if TYPE_CHECKING:
    from core.custom_bot import CustomBot
    from repositories.company_repository import CompanyRepository


class CompanyService:
    def __init__(self, companyRepository: "CompanyRepository", client: "CustomBot"):
        self.companyRepository = companyRepository
        self.client = client

    async def get_holiday_date_by_year(self, from_year: int, to_year: int) -> set[date]:
        holidays = await self.companyRepository.get_holiday_date_by_year(from_year, to_year)
        return holidays

    async def is_holiday_date(self, date: date) -> bool:
        holiday = await self.companyRepository.get_holiday_date_by_date(date)
        return holiday is not None

    async def get_holiday_days(
        self, from_date: date, to_date: date
    ) -> list[date]:
        holidays = await self.companyRepository.get_holidays_by_date_range(
            from_date=from_date, to_date=to_date
        )
        return [holiday.holiday_date for holiday in holidays]
    
    async def get_holiday_days_by_year(self, year: int) -> list[CompanyHoliday]:
        holidays = await self.companyRepository.get_holidays_by_year(year)
        return holidays
