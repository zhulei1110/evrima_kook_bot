import asyncio
import logging
from typing import TYPE_CHECKING

from khl import api

from .panel import main_panel
from ..utils.config import config

if TYPE_CHECKING:
    from ..tofu_bot import TofuBot

log = logging.getLogger(__name__)


async def on_startup(bot: 'TofuBot'):
    # bot.task.scheduler.add_job(
    #     restart,
    #     trigger='cron',
    #     hour='1,9,17',
    #     minute=50,
    #     second=0,
    #     args=(bot,)
    # )

    bot.task.scheduler.add_job(
        timed_announcement,
        trigger='cron',
        hour='*',
        args=(bot,)
    )

    # bot.task.scheduler.add_job(
    #     update_online_count,
    #     trigger='interval',
    #     minutes=1,
    #     args=(bot,)
    # )

    retry_rcon(bot)


def retry_rcon(bot):
    bot.task.scheduler.add_job(
        check_rcon,
        trigger='interval',
        seconds=5,
        id='check_rcon',
        args=(bot,)
    )


# async def restart(bot: 'TofuBot'):
#     bot.rcon.announce('Server restart in 10 mins, safelog Plz, 10 fen zhong hou chong qi!!!!!!!!!!!')
#     await asyncio.sleep(420)
#     bot.rcon.announce('Server restart in 3 mins, stop attack and safelog Plz, 3 fen zhong hou chong qi!!!!!!!!!!!')
#     await asyncio.sleep(120)
#     bot.rcon.announce('Server restart in 1 min, stop attack and safelog Plz, 1 fen zhong hou chong qi!!!!!!!!!!!')
#     await bot.restart_server()


async def timed_announcement(bot: 'TofuBot'):
    bot.rcon.announce(config.timed_announcement)


# async def update_online_count(bot: 'TofuBot'):
#     await bot.client.gate.exec_req(api.Message.update(
#         msg_id='43dc5d80-2523-4cc2-a8a8-a69bff2c6f07',
#         content=(await main_panel(bot, need_online_count=True)).build_to_json()
#     ))


async def check_rcon(bot: 'TofuBot'):
    if not bot.rcon.connected:
        try:
            if bot.rcon.connect():
                log.info('RCON connected successfully.')
                bot.task.scheduler.remove_job('check_rcon')
            else:
                log.error('RCON connecting failed.')
                bot.rcon.disconnect()
        except ConnectionRefusedError as e:
            log.error('RCON connecting failed: ', exc_info=e)
            bot.rcon.disconnect()
