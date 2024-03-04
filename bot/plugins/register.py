import logging
import datetime
from typing import TYPE_CHECKING

from khl import Message, EventTypes, Event

from .panel import info_panel
from ..database.models.user_info import UserInfo
from ..database.models.user_operation_log import UserOperationLog, UserOperationTypes
from ..utils.config import config
from ..utils.inventory import get_default_inventory
from ..utils.message import send_temp_message_with_channel

if TYPE_CHECKING:
    from ..tofu_bot import TofuBot

log = logging.getLogger(__name__)


async def on_startup(bot: 'TofuBot'):
    @bot.command(aliases=['注册'])
    async def register(msg: Message, steam_17: str):
        if await UserInfo.get_or_none(kook_id=msg.author.id):
            message = '您已经注册过了，不要重复注册。'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await UserOperationLog.create(kook_id=msg.author.id, steam_id=steam_17, operation_type=UserOperationTypes.REGISTER_USER, description=message, create_time=datetime.datetime.now())
            return
        if len(steam_17) != 17:
            message = 'Steam ID 不正确，请输入正确的17位 Steam ID。'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await UserOperationLog.create(kook_id=msg.author.id, steam_id=steam_17, operation_type=UserOperationTypes.REGISTER_USER, description=message, create_time=datetime.datetime.now())
            return

        if await UserInfo.get_or_none(steam_17_id=steam_17):
            message = '非常抱歉，该 Steam ID 已被注册。'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await UserOperationLog.create(kook_id=msg.author.id, steam_id=steam_17, operation_type=UserOperationTypes.REGISTER_USER, description=message, create_time=datetime.datetime.now())
            return

        await UserInfo.create(kook_id=msg.author.id, steam_17_id=steam_17, dragon_inventory=get_default_inventory(), create_date=datetime.datetime.now())

        message = '恭喜您，注册成功！'
        await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
        await UserOperationLog.create(kook_id=msg.author.id, steam_id=steam_17, operation_type=UserOperationTypes.REGISTER_USER, description=message, create_time=datetime.datetime.now())
        log.info(f'玩家 [{steam_17}] 注册成功。')

    @bot.on_event(EventTypes.EXITED_GUILD)
    async def exit_guild(_, event: Event):
        if event.target_id == config.guild_id:
            user_id = event.body['user_id']
            user = await bot.client.fetch_user(user_id)
            user_info = await UserInfo.get_or_none(kook_id=user_id)
            if user_info:
                await (await bot.client.fetch_user(config.owner_id)).send((await info_panel(user, False)).build())
                await user_info.delete()



