from datetime import date
from typing import TYPE_CHECKING, Optional

from models import CompanyHoliday

if TYPE_CHECKING:
    from db.asyncpg_client import AsyncpgClient


class CompanyRepository:
    def __init__(self, asyncpg_client: "AsyncpgClient"):
        self.asyncpg_client = asyncpg_client

    async def get_holidays_by_year(self, year: int) -> list[CompanyHoliday]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                "SELECT holiday_date, description FROM company_holidays WHERE EXTRACT(YEAR FROM holiday_date) = $1 ORDER BY holiday_date",
                year,
            )
            return [
                CompanyHoliday(
                    holiday_date=row["holiday_date"], description=row["description"]
                )
                for row in rows
            ]
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_holiday_date_by_year(
        self, from_year: int, to_year: int
    ) -> set[date]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                """
                SELECT holiday_date
                FROM company_holidays
                WHERE EXTRACT(YEAR FROM holiday_date) BETWEEN $1 AND $2
                ORDER BY holiday_date;
                """,
                from_year,
                to_year,
            )
            
            return {row["holiday_date"] for row in rows} if rows else set()
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_holiday_date_by_date(
        self, target_date: date
    ) -> Optional[CompanyHoliday]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            row = await conn.fetchrow(
                "SELECT holiday_date, description FROM company_holidays WHERE holiday_date = $1",
                target_date,
            )
            if row:
                return CompanyHoliday(
                    holiday_date=row["holiday_date"],
                    description=row["description"],
                )
            return None
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)

    async def get_holidays_by_date_range(
        self, from_date: date, to_date: date
    ) -> list[CompanyHoliday]:
        conn = None
        try:
            conn = await self.asyncpg_client.get_connection()
            rows = await conn.fetch(
                "SELECT holiday_date, description FROM company_holidays WHERE holiday_date BETWEEN $1 AND $2",
                from_date,
                to_date,
            )
            return [
                CompanyHoliday(
                    holiday_date=row["holiday_date"], description=row["description"]
                )
                for row in rows
            ]
        finally:
            if conn:
                await self.asyncpg_client.release_connection(conn)
