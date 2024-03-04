from typing import TYPE_CHECKING

from khl import Message, EventTypes, Event, Gateway, PrivateChannel
from khl_card import CardMessage, Card, Header

from .panels import main_panel, info_panel, dragon_egg_panel
from ..inventory.get_dragon import get_dragon
from ..inventory.save_dragon import save_dragon
from ...utils.message import update_private_message, update_message, check_can_use_bot, send_temp_message
# from ...database.models.user_info import UserInfo
# from ...database.models.refuse_user import RefuseUser

if TYPE_CHECKING:
    from ...tofu_bot import TofuBot


async def update(content, msg_id, user_id, gate: Gateway, is_private: bool):
    if is_private:
        await update_private_message(content, msg_id, gate)
    else:
        await update_message(content, msg_id, user_id, gate)

async def on_startup(bot: 'TofuBot'):
    @bot.command(aliases=['面板'])
    async def panel(msg: Message):
        data = await msg.ctx.channel.send(CardMessage(Card(Header('临时消息'))).build())

        is_private = isinstance(msg.ctx.channel, PrivateChannel)
        msg_id = data['msg_id']
            
        await update((await main_panel(bot, False, True, msg.author.id)).build(), msg_id, msg.author.id, bot.client.gate, is_private)

    @bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
    async def on_button_click(_, event: Event):
        value = event.body.get('value')
        msg_id = event.body.get('msg_id')
        user_id = event.body.get('user_id')
        target_id = event.body.get('target_id')
        is_private = event.body.get('channel_type') == 'PERSON'
        user = await bot.client.fetch_user(user_id)

        if not await check_can_use_bot(user_id):
            # await user.send('你无法使用本服服务')
            await send_temp_message('您已被拒绝使用机器人服务', user, target_id, is_private, bot)
            return

        if value == 'register':
            # await user.send('请在此使用命令 `/注册 steam17位id` 进行注册。请注意以 `/` 开头，另外 `注册` 后有空格。例如：`/注册 12345678901234567`')
            reg_msg = '请在此使用命令 `/注册 steam17位id` 进行注册。请注意以 `/` 开头，另外 `注册` 后有空格。例如：`/注册 12345678901234567`'
            await send_temp_message(reg_msg, user, target_id, is_private, bot)
        elif value == 'query':
            await update((await info_panel(user)).build(), msg_id, user_id, bot.client.gate, is_private)
        elif value == 'dragon_egg':
            await update((await dragon_egg_panel(user)).build(), msg_id, user_id, bot.client.gate, is_private)
        elif value == 'back_main':
            await update((await main_panel(bot, False, True, user_id)).build(), msg_id, user_id, bot.client.gate, is_private)
        elif value == 'save_dragon':
            await save_dragon(user_id, event.body['target_id'], is_private, bot)
        elif value == 'get_dragon':
            await get_dragon(user_id, event.body['target_id'], is_private, bot)
