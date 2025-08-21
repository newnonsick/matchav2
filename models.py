from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class StandupChannel(BaseModel):
    channel_id: str
    team_name: str
    server_id: str
    server_name: str
    timestamp: datetime


class StandupMessage(BaseModel):
    message_id: str
    author_id: str
    username: str
    servername: str
    channel_id: str
    content: str
    message_date: date
    timestamp: datetime
    last_updated_at: Optional[datetime] = None


class StandupMember(BaseModel):
    channel_id: str
    author_id: str
    server_name: str
    created_at: datetime


class LeaveRequest(BaseModel):
    message_id: str
    author_id: str
    channel_id: str
    content: str
    leave_type: Literal[
        "annual_leave", "sick_leave", "personal_leave", "birthday_leave"
    ]
    partial_leave: Optional[Literal["morning", "afternoon", "fullday"]]
    absent_date: date
    created_at: datetime


class DailyLeaveSummary(BaseModel):
    author_id: str
    leave_type: Literal[
        "annual_leave", "sick_leave", "personal_leave", "birthday_leave"
    ]
    partial_leave: Optional[Literal["morning", "afternoon", "fullday"]]
    team_name: str


class LeaveByDateChannel(BaseModel):
    author_id: str
    leave_type: Literal[
        "annual_leave", "sick_leave", "personal_leave", "birthday_leave"
    ]
    partial_leave: Optional[Literal["morning", "afternoon", "fullday"]]
    content: str


class UserStandupReport(BaseModel):
    content: str
    message_date: date
    timestamp: datetime
    last_updated_at: Optional[datetime] = None


class MemberTeam(BaseModel):
    author_id: str
    server_name: str


class LeaveInfo(BaseModel):
    absent_date: date
    leave_type: Literal[
        "annual_leave", "sick_leave", "personal_leave", "birthday_leave"
    ]
    partial_leave: Optional[Literal["morning", "afternoon", "fullday"]]


class LeaveRequestAnalysis(BaseModel):
    leave_request: list[LeaveInfo]


class Team(BaseModel):
    team_name: str
    server_id: str
    server_name: str
    channel_id: str


class OfficeEntry(BaseModel):
    author_id: str
    message_id: Optional[str]
    date: date
    created_at: datetime


class DailyOfficeEntrySummary(BaseModel):
    author_id: str
    server_name: str
    team_name: str


class CompanyHoliday(BaseModel):
    holiday_date: date
    description: str


class VoiceLog(BaseModel):
    id: Optional[int] = None
    author_id: str
    event_time: datetime
    event_type: Literal["join", "leave"]
    date: date


class DailyVoiceAttendance(BaseModel):
    author_id: str
    server_name: str
    status: Literal["weekend", "holiday", "leave", "on_time", "late", "absent"]


class StandupTask(BaseModel):
    id: Optional[UUID] = None
    message_id: str
    author_id: str
    task: str
    status: Literal["todo", "in_progress", "done"]
