import datetime
import logging
from typing import TYPE_CHECKING

from apscheduler.triggers.date import DateTrigger
from khl import Message, EventTypes, Event
from khl.card import CardMessage, Card, Module, Element

from ..database.models.user_voice_channel import UserVoiceChannel
from ..utils.config import config
from ..utils.rules import is_admin

if TYPE_CHECKING:
    from ..tofu_bot import TofuBot

log = logging.getLogger(__name__)


async def delete_voice_channel(bot: 'TofuBot', channel_id: str):
    await bot.client.delete_channel(channel_id)
    if db_channel := await UserVoiceChannel.get_or_none(channel_id=channel_id):
        await db_channel.delete()


async def on_startup(bot: 'TofuBot'):
    @bot.command('voice_card', aliases=['语音卡片'], rules=[is_admin])
    async def voice_card(msg: Message):
        cm = CardMessage(
            Card(
                Module.Section(
                    '单击右侧按钮，创建个人语音频道 -->',
                    accessory=Element.Button('创建', 'create_voice_channel')
                )
            )
        )
        await msg.ctx.channel.send(cm)

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def on_button_click(_, event: Event):
        value = event.body['value']
        user_id = event.body['user_id']

        if value != 'create_voice_channel':
            return

        button_channel = await bot.client.fetch_public_channel(event.body['target_id'])

        if await UserVoiceChannel.get_or_none(kook_id=user_id) is not None:
            await button_channel.send('您已拥有私人语音频道，不能重复创建！', temp_target_id=user_id)
            return

        guild = await bot.client.fetch_guild(config.guild_id)
        user = await guild.fetch_user(user_id)

        voice_channel = await guild.create_voice_channel(user.nickname, config.voice_parent_id)
        await voice_channel.create_user_permission(user.id)
        await voice_channel.update_user_permission(user.id, allow=415337512, deny=50331648)  # 编辑 用户 权限
        await voice_channel.update_role_permission('0', allow=8423424, deny=0)  # 编辑 @全体成员 权限

        await UserVoiceChannel.create(kook_id=user.id, channel_id=voice_channel.id)

        job_id = f'auto_delete_voice_channel_{user_id}'
        bot.task.scheduler.add_job(
            delete_voice_channel,
            trigger=DateTrigger(run_date=datetime.datetime.now() + datetime.timedelta(minutes=5)),
            args=(bot, voice_channel.id),
            id=job_id
        )

        await button_channel.send('私人语音频道创建成功！请在5分钟内加入，否则会自动删除。', temp_target_id=user_id)

    @bot.on_event(EventTypes.EXITED_CHANNEL)
    async def exited_voice_channel(_, event: Event):
        channel_id = event.body['channel_id']
        user_id = event.body['user_id']

        if await UserVoiceChannel.get_or_none(kook_id=user_id, channel_id=channel_id):
            # 当是数据库中存的频道，且是创建者，创建 7 秒后删除的任务
            job_id = f'auto_delete_voice_channel_{user_id}'
            bot.task.scheduler.add_job(
                delete_voice_channel,
                trigger=DateTrigger(run_date=datetime.datetime.now() + datetime.timedelta(seconds=7)),
                args=(bot, channel_id),
                id=job_id
            )

    @bot.on_event(EventTypes.JOINED_CHANNEL)
    async def joined_voice_channel(_, event: Event):
        channel_id = event.body['channel_id']
        user_id = event.body['user_id']

        if await UserVoiceChannel.get_or_none(kook_id=user_id, channel_id=channel_id):
            # 当是数据库中存的频道，且是创建者，删除 7 秒后删除的任务
            job_id = f'auto_delete_voice_channel_{user_id}'
            if (job := bot.task.scheduler.get_job(job_id)) is not None:
                job.remove()
