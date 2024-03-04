import logging
import os
import re
import datetime
from asyncio import Lock
from typing import TYPE_CHECKING

from ...database.models.user_info import UserInfo
from ...database.models.user_operation_log import UserOperationLog, UserOperationTypes
from ...utils.config import config
from ...utils.message import send_temp_message

if TYPE_CHECKING:
    from ...tofu_bot import TofuBot

log = logging.getLogger(__name__)
save_dragon_lock = Lock()


async def save_dragon(user_id: str, target_id: str, is_private: bool, bot: 'TofuBot'):
    await save_dragon_lock.acquire()
    user_info = await UserInfo.get_or_none(kook_id=user_id)
    if user_info is None:
        await send_temp_message('您无法使用存龙功能，请先注册用户！', user_id, target_id, is_private, bot)
        save_dragon_lock.release()
        return
    with open(config.game_log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    today_online = False
    is_line = 4
    dino = None
    growth = None
    for line in lines:
        if user_info.steam_17_id in line:
            today_online = True
        if 'Left The Server' in line and 'whilebeing' in line and user_info.steam_17_id in line:
            # 安全读秒
            is_line = 1
            match = re.search(r'Was playing as: (.+), Gender: .+, Growth: (.+)', line)
            if match:
                dino = match.group(1)
                growth = match.group(2)
        elif 'Left The Server' in line and user_info.steam_17_id in line:
            # 未安全读秒
            is_line = 2
        elif user_info.steam_17_id in line:
            # 在线
            is_line = 3

    if not today_online:
        msg = '系统未收录到您的数据，请确认您绑定的 Steam 账号是否进入本服游戏服务器。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return
    if is_line == 3:
        msg = '检测到您仍处于在线状态，若已下线请在重新读秒后尝试。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return
    if is_line != 1:
        msg = '存龙失败：您未安全读秒，请在安全读秒后执行此操作。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return

    if dino is None or growth is None:
        msg = '存龙失败：未找到你所存龙的种类和成长值。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return

    log.info(f'检测到玩家 [{user_info.steam_17_id}] 的龙：{dino}，成长值为：{growth}')

    if '0.750' not in growth:
        msg = '存龙失败：需要在龙的成长值达到 100% 后才可存龙。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return
    if dino is None:
        msg = '未能获取您保存的龙种，遇到此 BUG 请按照正确的步骤重新操作，并确认您绑定的 Steam 账号是否进入本服游戏服务器。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return
    if dino not in config.dragon_info:
        msg = f'存龙失败：未在机器人配置文件中找到龙：`{dino}`，遇到此 BUG 请确认您的操作步骤是否正确。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return
    dragon_info = config.dragon_info[dino]
    if dragon_info.count == -1:
        msg = f'非常抱歉，`{dragon_info.translate_name}` 暂不支持存龙。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return

    if dino not in user_info.dragon_inventory:
        user_info.dragon_inventory[dino] = 0
        await user_info.save()
    if user_info.dragon_inventory[dino] >= 1:
        msg = f'您的 `{dragon_info.translate_name}` 库存数量 ≥ 1只, 无法继续存龙。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return

    try:
        os.remove(f'{config.game_save_path}/{user_info.steam_17_id}.sav')
        os.remove(f'{config.game_save_path}/{user_info.steam_17_id}.sav.bak')
    except FileNotFoundError:
        log.error(f'未找到玩家 [{user_info.steam_17_id}] 的存档文件，存龙失败。')
        msg = '您已存龙成功，请勿重复点击存龙按钮。'
        await send_temp_message(msg, user_id, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())
        save_dragon_lock.release()
        return

    user_info.dragon_inventory[dino] += 1
    await user_info.save()
    msg = f'存龙成功：已为您添加了一个：`{dragon_info.translate_name}`'
    await send_temp_message(msg, user_id, target_id, is_private, bot)
    await UserOperationLog.create(kook_id=user_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.SAVE_DINOSAUR, description=msg, create_time=datetime.datetime.now())

    log.info(f'已为玩家 [{user_info.steam_17_id}] 成功录入1个：{dragon_info.translate_name}')
    save_dragon_lock.release()
