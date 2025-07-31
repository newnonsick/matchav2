from functools import wraps

import discord
from discord.ext import commands

from core.custom_bot import CustomBot


def is_admin():
    def decorator(func):
        @wraps(func)
        async def wrapper(
            self, obj: discord.Interaction | commands.Context, *args, **kwargs
        ):
            client: CustomBot | None = None
            if isinstance(obj, discord.Interaction) and isinstance(
                obj.client, CustomBot
            ):
                client = obj.client
            elif isinstance(obj, commands.Context) and isinstance(obj.bot, CustomBot):
                client = obj.bot
            if not client:
                return

            user = getattr(obj, "user", getattr(obj, "author", None))
            if user is None:
                return

            is_admin = await client.member_service.is_admin(user.id)
            if not is_admin:
                if isinstance(obj, discord.Interaction):
                    await obj.response.send_message(
                        "You do not have administrative privileges to perform this action.",
                        ephemeral=True,
                    )
                return

            return await func(self, obj, *args, **kwargs)

        return wrapper

    return decorator
