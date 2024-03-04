import asyncio
import logging
import datetime
from typing import TYPE_CHECKING, List

from khl import Message, User

from .panel import info_panel
from ..database.models.refuse_user import RefuseUser
from ..database.models.user_info import UserInfo
from ..database.models.admin_operation_log import AdminOperationLog, AdminOperationTypes
from ..utils.config import config
from ..utils.message import send_temp_message_with_channel
from ..utils.rules import is_admin, is_owner

if TYPE_CHECKING:
    from ..tofu_bot import TofuBot

log = logging.getLogger(__name__)


async def on_startup(bot: 'TofuBot'):
    # @bot.command(aliases=['重启'], rules=[is_owner])
    # async def restart(msg: Message, countdown: int = 60):
    #     await msg.reply('正在尝试重启服务器')
    #     await bot.restart_server(countdown)

    @bot.command(aliases=['查询'], rules=[is_admin])
    async def query(msg: Message, user_id: str):
        user_info = await UserInfo.get_or_none(kook_id=user_id)
        if user_info is None:
            user_info = await UserInfo.get_or_none(steam_17_id=user_id)
            if user_info is None:
                await send_temp_message_with_channel(msg.ctx.channel, f'查询失败，未找到该用户：{user_id}。', msg.author.id)
                return

        await send_temp_message_with_channel(
            msg.ctx.channel,
            (await info_panel(await bot.client.fetch_user(user_info.kook_id), False)).build(),
            msg.author.id
        )

    # @bot.command(aliases=['取龙'], rules=[is_admin])
    # async def get_dragon_cmd(msg: Message, steam_id: str):
    #     user_info = await UserInfo.get_or_none(steam_17_id=steam_id)
    #     if user_info is None:
    #         await send_temp_message_with_channel(msg.ctx.channel, f'未找到该用户：{steam_id}', msg.author.id)
    #         return

    #     # if user_info in get_dragon_list

    @bot.command(regex=r'/换绑 (\w{17}) (\w{17})', rules=[is_admin])
    async def rebind(msg: Message, old_id: str, new_id: str):
        user_info = await UserInfo.get_or_none(steam_17_id=old_id)
        if user_info is None:
            message = f'更换 Steam ID 失败，未找到该用户：{old_id}。'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_steam_id=old_id,
                operation_type=AdminOperationTypes.CHANGE_STEAM_ID,
                description=message,
                create_time=datetime.datetime.now())
            return

        user_info.steam_17_id = new_id
        await user_info.save()
        message = f'成功给用户 [{old_id}] 更换了新的 Steam ID：{new_id}。'
        await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
        await AdminOperationLog.create(
            admin_kook_id=msg.author.id,
            target_kook_id=user_info.kook_id,
            target_steam_id=user_info.steam_17_id,
            operation_type=AdminOperationTypes.CHANGE_STEAM_ID,
            description=message,
            create_time=datetime.datetime.now())
        ...

    @bot.command(rules=[is_admin])
    async def rcon(msg: Message):
        if not bot.rcon.connected:
            try:
                if bot.rcon.connect():
                    log.info('RCON connected successfully.')
                    await msg.reply('RCON 连接成功')
                else:
                    log.error('RCON connecting failed.')
                    bot.rcon.disconnect()
                    await msg.reply('RCON 连接失败')
            except ConnectionRefusedError as e:
                log.error('RCON connecting failed: ', exc_info=e)
                bot.rcon.disconnect()
                await msg.reply('RCON 连接失败')
        ...

    @bot.command(regex=r'(.*) (?:日志) (.*)', rules=[is_admin])
    async def log_date_data_kill(msg: Message, log_kind: str = '', in_put: str = ''):
        await msg.ctx.channel.send('---')
        with open(config.game_log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        log_text = ''
        is_send = 0
        for line in lines:
            if log_kind == '全部':
                await msg.ctx.channel.send('-->--')
                await msg.ctx.channel.send(f'> {line}')
                await asyncio.sleep(0.3)
            elif in_put in line and 'LogTheIsleKillData' in line and '击杀' in log_kind:
                log_text += line + "\n"
                if len(log_text) > 8000:
                    await msg.ctx.channel.send('-----------')
                    await msg.ctx.channel.send(f'> {log_text}')
                    log_text = ''
                    is_send = 1
                    await asyncio.sleep(0.3)
                else:
                    is_send = 0
            elif in_put in line and 'LogTheIsleJoinData' in line and '击杀' in log_kind:
                log_text += line + "\n"
                if len(log_text) > 8000:
                    await msg.ctx.channel.send('-----------')
                    await msg.ctx.channel.send(f'> {log_text}')
                    log_text = ''
                    is_send = 1
                    await asyncio.sleep(0.3)
                else:
                    is_send = 0
            elif in_put in line and 'LogTheIsleJoinData' in line and '上下线' in log_kind:
                log_text += line + "\n"
                if len(log_text) > 8000:
                    await msg.ctx.channel.send('-----------')
                    await msg.ctx.channel.send(f'> {log_text}')
                    log_text = ''
                    is_send = 1
                    await asyncio.sleep(0.3)
                else:
                    is_send = 0
            elif in_put in line and 'LogTheIsleKillData' in line and '死亡' in log_kind:
                log_text += line + "\n"
                if len(log_text) > 8000:
                    await msg.ctx.channel.send('-----------')
                    await msg.ctx.channel.send(f'> {log_text}')
                    log_text = ''
                    is_send = 1
                    await asyncio.sleep(0.3)
                else:
                    is_send = 0
            elif in_put in line and 'LogTheIsleChatData' in line and '聊天' in log_kind:
                log_text += line + "\n"
                if len(log_text) > 8000:
                    await msg.ctx.channel.send('-----------')
                    await msg.ctx.channel.send(f'> {log_text}')
                    log_text = ''
                    is_send = 1
                    await asyncio.sleep(0.3)
                else:
                    is_send = 0
            elif in_put in line and 'LogTheIsleCharacter' in line and '动作' in log_kind:
                log_text += line + "\n"
                if len(log_text) > 8000:
                    await msg.ctx.channel.send('-----------')
                    await msg.ctx.channel.send(f'> {log_text}')
                    log_text = ''
                    is_send = 1
                    await asyncio.sleep(0.3)
                else:
                    is_send = 0
            elif in_put in line and 'used command' in line and '管理' in log_kind:
                log_text += line + "\n"
                if len(log_text) > 8000:
                    await msg.ctx.channel.send('-----------')
                    await msg.ctx.channel.send(f'> {log_text}')
                    log_text = ''
                    is_send = 1
                    await asyncio.sleep(0.3)
                else:
                    is_send = 0
        if is_send == 0:
            await msg.ctx.channel.send('-----------')
            await msg.ctx.channel.send(f'> {log_text}')

        await msg.ctx.channel.send('---')

    @bot.command(name='ban', rules=[is_admin])
    async def ban(msg: Message, steam_17: str, reason: str, t: int):
        user_info = await UserInfo.get_or_none(steam_17_id=steam_17)
        if user_info is None:
            message = f'封禁 Steam 玩家失败，未找到该用户：{steam_17}。'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_steam_id=steam_17,
                operation_type=AdminOperationTypes.BAN_STEAM_USER,
                description=message,
                create_time=datetime.datetime.now())
            return
        
        bot.rcon.ban_player(steam_17, reason, t)
        message = f'成功使用 rcon 尝试封禁玩家 [{steam_17}] {t}小时。'
        await msg.reply(message)
        await AdminOperationLog.create(
            admin_kook_id=msg.author.id,
            target_kook_id=user_info.kook_id,
            target_steam_id=user_info.steam_17_id,
            operation_type=AdminOperationTypes.BAN_STEAM_USER,
            description=message,
            create_time=datetime.datetime.now())

    @bot.command(name='refuse', aliases=['拒绝'], rules=[is_admin])
    async def refuse(msg: Message, kook_id: str):
        user_info = await UserInfo.get_or_none(kook_id=kook_id)
        if user_info is None:
            message = f'拒绝提供服务失败，未找到该用户：{kook_id}。'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_kook_id=kook_id,
                operation_type=AdminOperationTypes.REFUSE_KOOK_USER,
                description=message,
                create_time=datetime.datetime.now())
            return
        
        await RefuseUser.get_or_create(kook_id=kook_id)
        message = f'已拒绝向用户 [{kook_id}] 提供所有服务。'
        await msg.reply(message)
        await AdminOperationLog.create(
            admin_kook_id=msg.author.id,
            target_kook_id=kook_id,
            operation_type=AdminOperationTypes.REFUSE_KOOK_USER,
            description=message,
            create_time=datetime.datetime.now())

    @bot.command(name='restore', aliases=['恢复'], rules=[is_admin])
    async def restore(msg: Message, kook_id: str):
        if refuse_user := await RefuseUser.get_or_none(kook_id=kook_id):
            await refuse_user.delete()
            message = f'已恢复用户 [{kook_id}] 使用所有服务。'
            await msg.reply(message)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_kook_id=kook_id,
                operation_type=AdminOperationTypes.RESTORE_KOOK_USER,
                description=message,
                create_time=datetime.datetime.now())
        else:
            message = f'恢复服务失败，用户 [{kook_id}] 不在封禁列表中。'
            await msg.reply(message)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_kook_id=kook_id,
                operation_type=AdminOperationTypes.RESTORE_KOOK_USER,
                description=message,
                create_time=datetime.datetime.now())

    @bot.command(name='show_non_bind', aliases=['显示无绑定'], rules=[is_admin])
    async def show_non_bind(msg: Message):
        guild = await bot.client.fetch_guild(config.guild_id)
        user_list = await guild.fetch_user_list()
        bot_user = await bot.client.fetch_me()

        non_bind_list = []  # type: List[User]

        for user in user_list:
            if user.id == bot_user.id:
                continue

            if await UserInfo.get_or_none(kook_id=user.id) is None:
                non_bind_list.append(user)

        await msg.reply('没有绑定注册 17 位的用户列表：')
        i = 0
        message_str = ''
        for user in non_bind_list:
            i += 1
            if i % 10 == 0:
                await msg.ctx.channel.send(message_str)
                message_str = ''
            message_str += f'{user.username}#{user.identify_num}({user.id})\n'

    # @bot.command(name='kick_non_bind', aliases=['踢出无绑定'], rules=[is_admin])
    # async def kick_non_bind(msg: Message):
    #     guild = await bot.client.fetch_guild(config.guild_id)
    #     user_list = await guild.fetch_user_list()
    #     bot_user = await bot.client.fetch_me()

    #     counter = 0

    #     for user in user_list:
    #         if user.id == bot_user.id:
    #             continue

    #         if await UserInfo.get_or_none(kook_id=user.id) is None:
    #             await guild.kickout(user)
    #             counter += 1

    #     await msg.reply(f'已踢出 {counter} 位未绑定用户')
