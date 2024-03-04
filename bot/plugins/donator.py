import logging
import datetime
from typing import TYPE_CHECKING

from khl import Message

from ..database.models.user_info import VipTypes, UserInfo
from ..database.models.admin_operation_log import AdminOperationLog, AdminOperationTypes
from ..utils.message import send_temp_message_with_channel
from ..utils.rules import is_owner, is_admin

if TYPE_CHECKING:
    from ..tofu_bot import TofuBot

log = logging.getLogger(__name__)


async def on_startup(bot: 'TofuBot'):
    @bot.command(regex=r'\/(.+)会员 (\w+) ?(\d+)?', rules=[is_admin])
    async def vip(msg: Message, vip_type: str, user_id: str, days: str = None):
        if days is not None:
            if days.isdigit():
                days = int(days)
            else:
                message = f"开通会员失败，`{days}` 不是一个正确的数字。"
                await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user_info.kook_id,
                    target_steam_id=user_info.steam_17_id,
                    operation_type=AdminOperationTypes.JOIN_VIP,
                    description=message,
                    create_time=datetime.datetime.now())

        if vip_type == '周':
            vip_type = VipTypes.WEEK
            days = 7 if days is None else days
        elif vip_type == '月':
            vip_type = VipTypes.MONTH
            days = 30 if days is None else days
        elif vip_type == '季':
            vip_type = VipTypes.QUARTER
            days = 90 if days is None else days
        elif vip_type == '年':
            vip_type = VipTypes.YEAR
            days = 360 if days is None else days
        elif vip_type == '永久':
            vip_type = VipTypes.PERMANENT
            days = 9999 if days is None else days
        else:
            message = f'开通会员失败，未知的会员类型 “{vip_type}”'
            await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_kook_id=user_info.kook_id,
                target_steam_id=user_info.steam_17_id,
                operation_type=AdminOperationTypes.JOIN_VIP,
                description=message,
                create_time=datetime.datetime.now())
            return

        user_info = await UserInfo.get_or_none(kook_id=user_id)
        if not user_info:
            user_info = await UserInfo.get_or_none(steam_17_id=user_id)
            if not user_info:
                message = f'给用户 [{user_id}] 开通会员失败，未找到该用户。'
                await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user_id,
                    target_steam_id=user_id,
                    operation_type=AdminOperationTypes.JOIN_VIP,
                    description=message,
                    create_time=datetime.datetime.now())
                return

        user_info.vip_days = days
        user_info.vip_type = vip_type
        await user_info.save()
        message = f'成功给用户 [{user_info.kook_id}] 开通了{vip_type.to_chinese()}会员{days}天。'
        await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
        await AdminOperationLog.create(
            admin_kook_id=msg.author.id,
            target_kook_id=user_info.kook_id,
            target_steam_id=user_info.steam_17_id,
            operation_type=AdminOperationTypes.JOIN_VIP,
            description=message,
            create_time=datetime.datetime.now())

    @bot.task.add_cron(hour=23, minute=59)
    async def add_vip_egg():
        """
        每天4点给vip发放龙蛋
        """
        user_infos = await UserInfo.all()
        for user_info in user_infos:
            if user_info.vip_days > 0:
                user_info.vip_days -= 1
                # 按VIP类型给龙蛋
                if user_info.vip_type == VipTypes.WEEK or user_info.vip_type == VipTypes.MONTH or user_info.vip_type == VipTypes.QUARTER:
                    user_info.dragon_egg += 1
                elif user_info.vip_type == VipTypes.YEAR:
                    user_info.dragon_egg += 2
                elif user_info.vip_type == VipTypes.PERMANENT:
                    user_info.dragon_egg += 3
                # 天数变为0时，VIP类型变为无
                if user_info.vip_days == 0:
                    user_info.vip_type = VipTypes.NONE

                await user_info.save()

            if user_info.monthly_card_days > 0:
                # 扣除月卡天数
                user_info.monthly_card_days -= 1
                await user_info.save()

    @bot.command(regex=r'\/孵化月卡 (\w+) ?(\d+)?', rules=[is_admin])
    async def monthly_card(msg: Message, user_id: str, days: str = None):
        if days is not None:
            if days.isdigit():
                days = int(days)
            else:
                message = f"开通孵化月卡失败，`{days}` 不是一个正确的数字。"
                await send_temp_message_with_channel(msg.ctx.channel, message, msg.author.id)
        if user := await UserInfo.get_or_none(kook_id=user_id):
            user.monthly_card_days = days if days is not None else user.monthly_card_days + 30
            if days is None:
                user.dragon_egg += 3
                message = f'成功给用户 [{user.kook_id}] 开通了30天孵化月卡，并赠送3枚龙蛋。'
                await msg.reply(message)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user.kook_id,
                    target_steam_id=user.steam_17_id,
                    operation_type=AdminOperationTypes.JOIN_HATCHING_MONTHLY_CARD,
                    description=message,
                    create_time=datetime.datetime.now())
            else:
                message = f'成功给用户 [{user.kook_id}] 的孵化月卡天数修改为{days}天。'
                await msg.reply(message)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user.kook_id,
                    target_steam_id=user.steam_17_id,
                    operation_type=AdminOperationTypes.JOIN_HATCHING_MONTHLY_CARD,
                    description=message,
                    create_time=datetime.datetime.now())
            await user.save()

        elif user := await UserInfo.get_or_none(steam_17_id=user_id):
            user.monthly_card_days = days if days is not None else user.monthly_card_days + 30
            if days is None:
                user.dragon_egg += 3
                message = f'成功给用户 [{user.kook_id}] 开通了30天孵化月卡，并赠送3枚龙蛋。'
                await msg.reply(message)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user.kook_id,
                    target_steam_id=user.steam_17_id,
                    operation_type=AdminOperationTypes.JOIN_HATCHING_MONTHLY_CARD,
                    description=message,
                    create_time=datetime.datetime.now())
            else:
                message = f'成功给用户 [{user.kook_id}] 的孵化月卡天数修改为{days}天。'
                await msg.reply(message)
                await AdminOperationLog.create(
                    admin_kook_id=msg.author.id,
                    target_kook_id=user.kook_id,
                    target_steam_id=user.steam_17_id,
                    operation_type=AdminOperationTypes.JOIN_HATCHING_MONTHLY_CARD,
                    description=message,
                    create_time=datetime.datetime.now())
            await user.save()

        else:
            message = f'给用户 [{user_id}] 开通孵化月卡失败，未找到该用户。'
            await msg.reply(message)
            await AdminOperationLog.create(
                admin_kook_id=msg.author.id,
                target_kook_id=user_id,
                target_steam_id=user_id,
                operation_type=AdminOperationTypes.JOIN_HATCHING_MONTHLY_CARD,
                description=message,
                create_time=datetime.datetime.now())
            return
