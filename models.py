from typing import Literal, Optional

from pydantic import BaseModel


class StandupChannel(BaseModel):
    channel_id: str
    team_name: str
    server_id: str
    server_name: str
    timestamp: str


class StandupMessage(BaseModel):
    message_id: str
    author_id: str
    username: str
    servername: str
    channel_id: str
    content: str
    timestamp: str


class StandupMember(BaseModel):
    channel_id: str
    author_id: str
    server_name: str
    created_at: str


class LeaveRequest(BaseModel):
    message_id: str
    author_id: str
    channel_id: str
    content: str
    leave_type: Literal[
        "annual_leave", "sick_leave", "personal_leave", "birthday_leave"
    ]
    partial_leave: Optional[Literal["morning", "afternoon", "fullday"]]
    absent_date: str
    created_at: str


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
    timestamp: str


class MemberTeam(BaseModel):
    author_id: str
    server_name: str


class LeaveInfo(BaseModel):
    absent_date: str
    leave_type: Literal[
        "annual_leave", "sick_leave", "personal_leave", "birthday_leave"
    ]
    partial_leave: Optional[Literal["morning", "afternoon", "fullday"]]


class LeaveRequestAnalysis(BaseModel):
    leave_request: list[LeaveInfo]
