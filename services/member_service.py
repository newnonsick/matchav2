from models import MemberTeam
from repositories.member_repository import MemberRepository


class MemberService:
    def __init__(self, member_repository: MemberRepository):
        self.member_repository = member_repository

    async def get_all_standup_members(self) -> list[MemberTeam]:
        return await self.member_repository.get_all_standup_members()

    async def get_standup_members_by_channelid(
        self, channel_id: int
    ) -> list[MemberTeam]:
        return await self.member_repository.get_standup_members_by_channelid(
            str(channel_id)
        )
