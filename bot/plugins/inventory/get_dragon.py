import datetime
import logging
from asyncio import Lock
from typing import TYPE_CHECKING, Dict

from khl import api
from khl_card import CardMessage, Card, Section, Kmarkdown

from .util import get_player_dino_kind
from ...database.models.user_info import UserInfo
from ...database.models.user_operation_log import UserOperationLog, UserOperationTypes
from ...utils.config import config
from ...utils.message import send_temp_message

if TYPE_CHECKING:
    from ...tofu_bot import TofuBot

log = logging.getLogger(__name__)


class GetDragonInfo:

    def __init__(self, msg_id: str, steam_id: str, time: datetime.datetime) -> None:
        self.msg_id = msg_id
        self.steam_id = steam_id
        self.time = time


# 等待取龙列表 Dict[kook_id, msg_id]
get_dragon_list: Dict[str, GetDragonInfo] = {}
get_dragon_lock = Lock()


async def get_dragon(user_id: str, target_id: str, is_private: bool, bot: 'TofuBot'):
    await get_dragon_lock.acquire()
    user_info = await UserInfo.get_or_none(kook_id=user_id)
    if user_info is None:
        await send_temp_message('您无法使用取龙功能，请先注册用户！', user_id, target_id, is_private, bot)
        get_dragon_lock.release()
        return
    with open(config.game_log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    need_get = True
    for line in lines:
        if user_info.steam_17_id in line and 'Joined The Server' in line and 'Growth: 0.750' in line:
            need_get = False
        elif user_info.steam_17_id in line and 'Growth:' in line and '0.750' not in line:
            need_get = True
        elif user_info.steam_17_id in line and 'used command: Grow at' in line and 'New value: 0.750' in line:
            need_get = False
        elif user_info.steam_17_id in line and ('Growth: 0.750' in line or 'Growth: 1.000000' in line):
            need_get = False

    if not need_get:
        msg = '您的龙已经成年，无法取龙。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.GET_DINOSAUR_REQUEST, description=msg, create_time=datetime.datetime.now())
        get_dragon_lock.release()
        return

    dino, growth = get_player_dino_kind(user_info.steam_17_id)
    if dino is None:
        msg = '未能获取您保存的龙种，遇到此 BUG 请按照正确的步骤重新操作，并确认您绑定的 Steam 账号是否进入本服游戏服务器。'
        await send_temp_message('', user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.GET_DINOSAUR_REQUEST, description=msg, create_time=datetime.datetime.now())
        get_dragon_lock.release()
        return
    if dino not in config.dragon_info:
        msg = f'录入失败：未在机器人配置文件中找到龙：{dino}, 遇到此 BUG 请确认您的操作步骤是否正确。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.GET_DINOSAUR_REQUEST, description=msg, create_time=datetime.datetime.now())
        get_dragon_lock.release()
        return
    dragon_info = config.dragon_info[dino]

    if user_info.kook_id in get_dragon_list:
        await send_temp_message('您已经提交了取龙申请，请耐心等待。', user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.GET_DINOSAUR_REQUEST, description=msg, create_time=datetime.datetime.now())
        get_dragon_lock.release()
        return

    if dino not in user_info.dragon_inventory:
        user_info.dragon_inventory[dino] = 0

    if user_info.dragon_inventory[dino] < 1:
        msg = f'您的 `{dragon_info.translate_name}` 库存不足，无法取龙。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.GET_DINOSAUR_REQUEST, description=msg, create_time=datetime.datetime.now())
        get_dragon_lock.release()
        return

    ch = await bot.client.fetch_public_channel(config.get_dragon_channel)
    request_card = CardMessage(Card(
        Section(
            Kmarkdown.at_user('all') + 
            Kmarkdown(f'收到玩家的取龙申请，Steam ID：{user_info.steam_17_id}，KOOK User: ') + 
            Kmarkdown.at_user(user_info.kook_id)
        ))).build()
    msg_id = (await ch.send(request_card))['msg_id']
    get_dragon_list[user_info.kook_id] = GetDragonInfo(msg_id=msg_id, steam_id=user_info.steam_17_id, time=datetime.datetime.now())

    bot.task.scheduler.add_job(
        time_out,
        'date',
        run_date=datetime.datetime.now() + datetime.timedelta(minutes=3),
        id=f'get_dragon_{user_info.kook_id}',
        misfire_grace_time=10,
        args=(bot, user_info, msg_id),
        timezone='Asia/Shanghai'
    )

    get_dragon_lock.release()


async def time_out(bot: 'TofuBot', user_info: UserInfo, msg_id: str):
    if user_info.kook_id not in get_dragon_list:
        return
    timeout_card = CardMessage(Card(Section(Kmarkdown(f'Steam ID：{user_info.steam_17_id} 的取龙申请已经过期，无需点大。'))))
    await bot.client.gate.exec_req(api.Message.update(msg_id=msg_id, content=timeout_card.build_to_json()))

    get_dragon_list.pop(user_info.kook_id)
