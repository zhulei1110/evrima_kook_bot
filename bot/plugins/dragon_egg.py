import datetime
import logging
import random
import re
from asyncio import Lock
from typing import TYPE_CHECKING

from khl import EventTypes, Event, User, Message

from ..database.models.user_info import UserInfo
from ..database.models.user_operation_log import UserOperationLog, UserOperationTypes
from ..database.models.admin_operation_log import AdminOperationLog, AdminOperationTypes
from ..utils.config import config
from ..utils.message import send_temp_message, send_temp_message_with_channel, check_can_use_bot
from ..utils.rules import is_owner, is_admin

if TYPE_CHECKING:
    from ..tofu_bot import TofuBot

log = logging.getLogger(__name__)

hatch_lock = Lock()


async def on_startup(bot: 'TofuBot'):
    @bot.command(aliases=['龙蛋'], rules=[is_admin])
    async def dragon_egg(msg: Message, user_id: str, count: int):
        user_info = await UserInfo.get_or_none(kook_id=user_id)
        if user_info is None:
            user_info = await UserInfo.get_or_none(steam_17_id=user_id)
            if user_info is None:
                message = f'给用户 [{user_id}] 添加龙蛋失败，未找到该用户。'
                await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user_id,
                    target_steam_id=user_id,
                    operation_type=AdminOperationTypes.ADD_DINOSAUR_EGG,
                    description=message,
                    create_time=datetime.datetime.now())
                return

        user_info.dragon_egg += count
        await user_info.save()
        message = f'成功给用户 [{user_id}] 添加了{count}个龙蛋。'
        log.info(message)
        await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
        await AdminOperationLog.create(
            admin_kook_id=msg.author.id,
            target_kook_id=user_info.kook_id,
            target_steam_id=user_info.steam_17_id,
            operation_type=AdminOperationTypes.ADD_DINOSAUR_EGG,
            description=message,
            create_time=datetime.datetime.now())

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def buy_dragon(_, event: Event):

        value = event.body.get('value')  # type: str
        msg_id = event.body.get('msg_id')
        user_id = event.body.get('user_id')
        target_id = event.body.get('target_id')
        is_private = event.body.get('channel_type') == 'PERSON'

        user = await bot.client.fetch_user(user_id)

        if not await check_can_use_bot(user_id):
            await user.send('您已被拒绝使用机器人服务')
            return

        match = re.match(r'buy_(\w+)', value)
        if match:
            dragon_name = match.group(1)
            dragon_info = config.dragon_info.get(dragon_name, None)
            if dragon_info:
                user_info = await UserInfo.get_or_none(kook_id=user_id)

                if user_info.dragon_egg >= dragon_info.cost:
                    user_info.dragon_egg -= dragon_info.cost
                    if dragon_name not in user_info.dragon_inventory:
                        user_info.dragon_inventory[dragon_name] = 0
                    user_info.dragon_inventory[dragon_name] += dragon_info.count
                    await user_info.save()
                    log.info(f'玩家 [{user_info.steam_17_id}] 使用 {dragon_info.cost} 龙蛋兑换了{dragon_info.count}只{dragon_info.translate_name}')
                    message = f'恭喜您！成功兑换了{dragon_info.count}只 `{dragon_info.translate_name}`。'
                    await send_temp_message(message, user, target_id, is_private, bot)
                    await UserOperationLog.create(kook_id=user_info.kook_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.BUG_DINOSAUR, description=message, create_time=datetime.datetime.now())
                else:
                    message = f'抱歉，兑换 `{dragon_info.translate_name}` 失败，剩余龙蛋不足！'
                    await send_temp_message(message, user, target_id, is_private, bot)
                    await UserOperationLog.create(kook_id=user_info.kook_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.BUG_DINOSAUR, description=message, create_time=datetime.datetime.now())
        elif value == 'hatch':
            await hatch_egg(user, target_id, is_private, bot)
        # elif value == 'open_egg':
        #     await open_egg(user, target_id, is_private, bot)


async def hatch_egg(user: User, target_id, is_private, bot: 'TofuBot'):
    await hatch_lock.acquire()
    user_info = await UserInfo.get_or_none(kook_id=user.id)
    if not user_info:
        await send_temp_message('您无法使用孵化功能，请先注册用户！', user, target_id, is_private, bot)
        hatch_lock.release()
        return

    now_time = datetime.datetime.now()
    now_time_str = now_time.strftime('%Y-%m-%d')
    last_time_str = user_info.last_dragon_egg_hatch_date.strftime('%Y-%m-%d') if user_info.last_dragon_egg_hatch_date is not None else ''
    monthly_card_last_time_str = user_info.last_monthly_card_hatch_date.strftime('%Y-%m-%d') if user_info.last_monthly_card_hatch_date else ''

    if now_time_str != last_time_str:
        random_hatch = random.randint(1, 20)
        if user_info.dragon_egg_hatch_percent + random_hatch < 100:
            user_info.dragon_egg_hatch_percent += random_hatch
            log.info(f'玩家 [{user_info.steam_17_id}] 获得了 {random_hatch}% 的孵化进度')
            msg = f'您获得了 {random_hatch}% 的孵化进度，您当前总进度为: {user_info.dragon_egg_hatch_percent}%。'
            await send_temp_message(msg, user, target_id, is_private, bot)
            await UserOperationLog.create(kook_id=user_info.kook_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.HATCHING_DINOSAUR_EGG, description=msg, create_time=datetime.datetime.now())
        else:
            user_info.dragon_egg_hatch_percent = 0
            user_info.dragon_egg += 1
            log.info(f'玩家 [{user_info.steam_17_id}] 孵化值达到100%，获得1个龙蛋')
            msg = '恭喜您！您当前孵化值达到100%，获得1个龙蛋，已自动加入库存。'
            await send_temp_message(msg, user, target_id, is_private, bot)
            await UserOperationLog.create(kook_id=user_info.kook_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.HATCHING_DINOSAUR_EGG, description=msg, create_time=datetime.datetime.now())
        user_info.last_dragon_egg_hatch_date = now_time
        await user_info.save()
    elif now_time_str != monthly_card_last_time_str and user_info.monthly_card_days > 0:
        random_hatch = random.randint(1, 20)
        if user_info.dragon_egg_hatch_percent + random_hatch < 100:
            user_info.dragon_egg_hatch_percent += random_hatch
            log.info(f'玩家 [{user_info.steam_17_id}] 获得了 {random_hatch}% 的孵化进度')
            msg = f'您获得了 {random_hatch}% 的孵化进度，您当前总孵化进度为: {user_info.dragon_egg_hatch_percent}%'
            await send_temp_message(msg, user, target_id, is_private, bot)
            await UserOperationLog.create(kook_id=user_info.kook_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.HATCHING_DINOSAUR_EGG, description=msg, create_time=datetime.datetime.now())
        else:
            user_info.dragon_egg_hatch_percent = 0
            user_info.dragon_egg += 1
            log.info(f'玩家 [{user_info.steam_17_id}] 孵化值达到100%，获得1个龙蛋')
            msg = '恭喜您！您当前孵化值达到100%，获得1个龙蛋，已自动加入库存。'
            await send_temp_message(msg, user, target_id, is_private, bot)
            await UserOperationLog.create(kook_id=user_info.kook_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.HATCHING_DINOSAUR_EGG, description=msg, create_time=datetime.datetime.now())
        user_info.last_monthly_card_hatch_date = now_time
        await user_info.save()
    else:
        msg = '您今日已经孵化过了！开通 `孵化月卡` 每天可孵化 2次 哟~'
        await send_temp_message(msg, user, target_id, is_private, bot)
        await UserOperationLog.create(kook_id=user_info.kook_id, steam_id=user_info.steam_17_id, operation_type=UserOperationTypes.HATCHING_DINOSAUR_EGG, description=msg, create_time=datetime.datetime.now())
    hatch_lock.release()


# async def open_egg(user: User, target_id, is_private, bot: 'TofuBot'):
#     user_info = await UserInfo.get_or_none(kook_id=user.id)
#     if not user_info:
#         await send_temp_message('请注册后使用这个功能！', user, target_id, is_private, bot)
#         return

#     if user_info.dragon_egg < 1:
#         await send_temp_message('您的库存龙蛋数量不足！', user, target_id, is_private, bot)
#         return

#     user_info.dragon_egg -= 1

#     total_weigh = 0
#     for pool in config.dragon_gacha:
#         total_weigh += pool.weigh

#     random_int = random.randint(1, total_weigh)
#     for pool in config.dragon_gacha:
#         if random_int <= pool.weigh:
#             rewards = pool.dragons
#             reward = random.choice(rewards)

#             if reward in config.dragon_info:
#                 if reward not in user_info.dragon_inventory:
#                     user_info.dragon_inventory[reward] = 0
#                 user_info.dragon_inventory[reward] += 1
#                 await user_info.save()
#                 log.info(f'[{user_info.steam_17_id}] 开出了 {reward}')
#                 await send_temp_message(f'开蛋成功！恭喜您开出了 {config.dragon_info[reward].translate_name}',
#                                         user, target_id, is_private, bot)
#             else:
#                 await send_temp_message(f'请联系管理员确认奖池是否填写正确，未找到叫做 {reward} 的龙！')
#             break
#         else:
#             random_int -= pool.weigh
