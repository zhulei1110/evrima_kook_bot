import datetime
import logging
import re
from typing import TYPE_CHECKING

from khl import Message, api
from khl_card import CardMessage, Card, Section, Kmarkdown

from .get_dragon import get_dragon_list
from ...database.models.user_info import UserInfo
from ...database.models.admin_operation_log import AdminOperationLog, AdminOperationTypes
from ...utils.config import config
from ...utils.message import send_temp_message_with_channel
from ...utils.rules import is_owner, is_admin

if TYPE_CHECKING:
    from ...tofu_bot import TofuBot

log = logging.getLogger(__name__)


async def on_startup(bot: 'TofuBot'):
    @bot.command(aliases=['库存'], rules=[is_admin])
    async def inventory(msg: Message, user_id: str, dragon_type: str, count: int):
        user_info = await UserInfo.get_or_none(kook_id=user_id)
        if user_info is None:
            user_info = await UserInfo.get_or_none(steam_17_id=user_id)
            if user_info is None:
                text_msg = f'增加库存失败，未找到该用户：{user_id}。'
                await send_temp_message_with_channel(msg.ctx.channel, text_msg, msg.author.id)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user_id,
                    target_steam_id=user_id,
                    operation_type=AdminOperationTypes.ADD_DINOSAUR_INVENTORY,
                    description=text_msg,
                    create_time=datetime.datetime.now())
                return

        if dragon_type == '所有龙':
            for name in config.dragon_info:
                if name not in user_info.dragon_inventory:
                    user_info.dragon_inventory[name] = 0
                user_info.dragon_inventory[name] += count
            await user_info.save()
            message = f'成功给用户 [{user_id}] 的所有龙的库存数量增加{count}。'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_kook_id=user_info.kook_id,
                target_steam_id=user_info.steam_17_id,
                operation_type=AdminOperationTypes.ADD_DINOSAUR_INVENTORY,
                description=message,
                create_time=datetime.datetime.now())
            log.info(message)
        else:
            dragon_name = None
            for name in config.dragon_info:
                if name.startswith(dragon_type):
                    if dragon_name is not None:
                        message = f'增加库存失败，根据输入的名称[{dragon_type}]找到了多种恐龙，请使用更长的原名。'
                        await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
                        await AdminOperationLog.create(
                            admin_kook_id=msg.author.id,
                            target_kook_id=user_info.kook_id,
                            target_steam_id=user_info.steam_17_id,
                            operation_type=AdminOperationTypes.ADD_DINOSAUR_INVENTORY,
                            description=message,
                            create_time=datetime.datetime.now())
                        return
                    else:
                        dragon_name = name

            if dragon_name is not None:
                if dragon_name not in user_info.dragon_inventory:
                    user_info.dragon_inventory[dragon_name] = 0
                user_info.dragon_inventory[dragon_name] += count

                message = f'成功给用户 [{user_id}] 的{config.dragon_info[dragon_name].translate_name}库存数量增加{count}。'
                await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user_info.kook_id,
                    target_steam_id=user_info.steam_17_id,
                    operation_type=AdminOperationTypes.ADD_DINOSAUR_INVENTORY,
                    description=message,
                    create_time=datetime.datetime.now())
                log.info(message)

                await user_info.save()
            else:
                message = f'增加库存失败，根据输入的名称[{dragon_type}]没有找到匹配的恐龙，请确认名称是否正确。'
                await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user_info.kook_id,
                    target_steam_id=user_info.steam_17_id,
                    operation_type=AdminOperationTypes.ADD_DINOSAUR_INVENTORY,
                    description=message,
                    create_time=datetime.datetime.now())

    bot.task.scheduler.add_job(get_dragon_check, 'interval', seconds=5, args=(bot,), max_instances=1)


async def get_dragon_check(bot: 'TofuBot'):
    if len(get_dragon_list) == 0:
        return
    with open(config.game_log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    while len(lines) != 0:
        text = lines.pop()
        if 'command: Grow' in text:
            for kook_id in list(get_dragon_list.keys()):
                info = get_dragon_list[kook_id]
                if info.steam_id in text and '0.750' in text:
                    ctime = text[1:20]
                    log.info('日志点大时间：%s', ctime)
                    log.info('取龙请求时间：%s', info.time.strftime('%Y.%m.%d-%H.%M.%S'))
                    if (datetime.datetime.strptime(ctime, '%Y.%m.%d-%H.%M.%S') + datetime.timedelta(hours=8)) < info.time:
                        break

                    user_info = await UserInfo.get_or_none(kook_id=kook_id)
                    finds = re.findall(r'\[(\d{17})], Class: (.+), G.+New value: (.+)%', text)
                    if len(finds) == 0:
                        break
                    dino = finds[0][1]
                    if dino not in config.dragon_info:
                        log.error('取龙找到不在配置文件中的龙！')
                        break

                    dragon_info = config.dragon_info[dino]
                    if dino not in user_info.dragon_inventory:
                        user_info.dragon_inventory[dino] = 0
                    user_info.dragon_inventory[dino] -= 1

                    if user_info.dragon_inventory[dino] < 0:
                        await (await bot.client.fetch_user(config.owner_id)).send(
                            f'用户 [{user_info.steam_17_id}] {dino} 库存数量小于0，请及时调整'
                        )
                        await (await bot.client.fetch_user(user_info.kook_id)).send(
                            f'您的 {dragon_info.translate_name} 为库存数量小于0，管理已撤回点大，并给您库存恢复正常'
                        )

                    c = CardMessage(Card(Section(Kmarkdown(
                        f'steamid: {info.steam_id} 检测到点大成功，已扣除 {dragon_info.translate_name} 1只。'
                    ))))

                    await (await bot.client.fetch_user(kook_id)).send(
                        f'steamid: {info.steam_id} 检测到点大成功，已扣除 {dragon_info.translate_name} 1只。'
                    )
                    log.info(f'steamid: {info.steam_id} 检测到点大成功，已扣除 {dragon_info.translate_name} 1只。')
                    await bot.client.gate.exec_req(api.Message.update(msg_id=info.msg_id, content=c.build_to_json()))

                    # 移除超时任务
                    if bot.task.scheduler.get_job(f'get_dragon_{user_info.kook_id}'):
                        bot.task.scheduler.remove_job(f'get_dragon_{user_info.kook_id}')
                    del get_dragon_list[kook_id]
                    await user_info.save()
