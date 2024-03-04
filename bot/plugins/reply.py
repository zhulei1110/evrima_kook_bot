import logging
from typing import TYPE_CHECKING

from khl import EventTypes, Event, MessageTypes, Message

from ..utils.config import config

if TYPE_CHECKING:
    from ..tofu_bot import TofuBot

log = logging.getLogger(__name__)


async def on_startup(bot: 'TofuBot'):
    # 用户加入服务器事件处理
    @bot.on_event(EventTypes.JOINED_GUILD)
    async def on_join_guild(_, event: Event):
        if event.target_id == config.guild_id:
            user = await bot.client.fetch_user(event.extra['user_id'])
            await user.send(config.welcome_message)

    # 自定义回复
    @bot.on_message(MessageTypes.IMG, MessageTypes.CARD, MessageTypes.FILE, MessageTypes.AUDIO)
    async def on_message(msg: Message):
        for word_str in config.replies.keys():
            word_list = word_str.split(',')
            if any(word in msg.content for word in word_list):
                await msg.reply(config.replies.get(word_str))
                break
