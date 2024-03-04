import json
from typing import Union

from khl import Channel, PublicTextChannel, Gateway, api, User, Bot

from ..database.models.refuse_user import RefuseUser


async def check_can_use_bot(kook_id: str) -> bool:
    return (await RefuseUser.get_or_none(kook_id=kook_id)) is None


async def send_temp_message_with_channel(channel: Channel, msg: str, author_id: str):
    if isinstance(channel, PublicTextChannel):
        await channel.send(msg, temp_target_id=author_id)
    else:
        await channel.send(msg)


async def send_temp_message(content, user: Union[User, str], target_id: str, is_private: bool, bot: Bot):
    user = user if isinstance(user, User) else await bot.client.fetch_user(user)
    if is_private:
        await user.send(content)
        return
    else:
        channel = await bot.client.fetch_public_channel(target_id)
        if isinstance(channel, PublicTextChannel):
            await channel.send(content, temp_target_id=user.id)


async def update_message(content, msg_id: str, user_id: str, gate: Gateway):
    content = content if isinstance(content, str) else json.dumps(content)
    await gate.exec_req(api.Message.update(msg_id=msg_id, content=content, temp_target_id=user_id))


async def update_private_message(content, msg_id: str, gate: Gateway):
    content = content if isinstance(content, str) else json.dumps(content)
    await gate.exec_req(api.DirectMessage.update(msg_id=msg_id, content=content))
