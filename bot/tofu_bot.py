import asyncio
import importlib
# import locale
import logging
import os
# from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
# from threading import Thread
from types import ModuleType
from typing import List

# import psutil
from khl import Bot

from . import database
# from .plugins.tasks import retry_rcon
from .utils.config import config
from .utils.function import has_and_is_coroutine_function
from .utils.rcon import RconConnection

log = logging.getLogger(__name__)


# class ServerPipeThread(Thread):

#     def __init__(self, bot: 'TofuBot') -> None:
#         super().__init__(name="ServerThread")

#         self.flag = True
#         self.bot = bot
#         self.process = Popen(config.server_command, cwd=config.server_path, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
#                              shell=True)
#         self.start()

#     def run(self) -> None:
#         while self.flag:
#             # server loop
#             try:
#                 text: bytes = next(iter(self.process.stdout))
#             except StopIteration:
#                 # 最多等待60秒
#                 for i in range(60):
#                     try:
#                         self.process.wait(1)
#                     except TimeoutExpired:
#                         log.error("Waiting for server process to stop")
#                     else:
#                         break
#                 else:
#                     log.warning('The server is still not stopped after 60s after its stdout was closed.')
#             else:
#                 try:
#                     decoded_text: str = text.decode(locale.getpreferredencoding())
#                 except Exception as e:
#                     log.error('Fail to decode text %s: %s', text, e)
#                     continue
#                 # print('[server] ' + decoded_text.rstrip('\n\r').lstrip('\n\r'))
#                 self.bot.on_receive(decoded_text.rstrip('\n\r').lstrip('\n\r'))

#     def kill_server(self):
#         self.flag = False
#         if self.process and self.process.poll() is None:
#             log.info("Killing the server...")
#             try:
#                 root = psutil.Process(self.process.pid)
#                 processes = [root]
#                 processes.extend(root.children(recursive=True))
#                 for proc in reversed(processes):
#                     try:
#                         proc_pid, proc_name = proc.pid, proc.name()
#                         proc.kill()
#                         log.info('Process %s (pid %d) killed', proc_name, proc_pid)
#                     except psutil.NoSuchProcess:
#                         pass
#             except psutil.NoSuchProcess:
#                 pass
#             self.process.poll()
#         else:
#             log.warning('Try to kill the server when the server process has already been terminated')
#         self.bot.rcon.disconnect()


class TofuBot(Bot):

    def __init__(self):
        super().__init__(config.token)

        self._modules: List[ModuleType] = []

        # self.server_thread = ServerPipeThread(self)
        self.rcon = RconConnection(config.rcon_address, config.rcon_port, config.rcon_password)

        self.on_startup(self.on_my_bot_startup)
        self.on_shutdown(self.on_my_bot_shutdown)

        # self.task.add_interval(minutes=5)(self.check_server_alive)

    async def load_plugins(self):
        log.info('Loading plugins...')

        modules = []
        for file in os.listdir('bot/plugins'):
            if not file.startswith('__'):
                name, ext = os.path.splitext(file)
                modules.append('.' + name)

        loaded_count = 0

        for module_name in modules:
            module = importlib.import_module(module_name, 'bot.plugins')
            func = has_and_is_coroutine_function(module, 'on_startup')
            if func:
                await func(self)
                loaded_count += 1
                self._modules.append(module)
                log.info(f'Plugin {module_name[1:]} loaded successfully.')
            else:
                log.error(f'Plugin {module_name[1:]} loading failed.')

        log.info(f'Successfully loaded {loaded_count} plugins')

    async def on_my_bot_startup(self, _: Bot):
        await database.connect()
        await self.load_plugins()

    async def on_my_bot_shutdown(self, _: Bot):
        await database.disconnect()
        # self.server_thread.kill_server()
        self.rcon.disconnect()
        log.info('RCON disconnected successfully.')

    # def on_receive(self, text: str):
    #     print(text)
    #     if 'with flag success' in text:
    #         if config.rcon_enabled and not self.rcon.connected:
    #             try:
    #                 if self.rcon.connect():
    #                     log.info('RCON connected successfully.')
    #                 else:
    #                     log.error('RCON connecting failed.')
    #                     self.rcon.disconnect()
    #             except ConnectionRefusedError as e:
    #                 log.error('RCON connecting failed: ', exc_info=e)
    #                 self.rcon.disconnect()

    #     if 'command: Grow' in text:
    #         for module in self._modules:
    #             func = has_and_is_coroutine_function(module, 'on_receive')
    #             if func:
    #                 asyncio.run(func(self, text))

    # async def restart_server(self, countdown: int = 60):
    #     self.rcon.announce(f'Server restart in {countdown} seconds...')
    #     if countdown > 5:
    #         await asyncio.sleep(countdown - 5)
    #     for i in reversed(range(5)):
    #         self.rcon.announce(f'Server restart in {i + 1} seconds...')
    #         await asyncio.sleep(1)
    #     self.server_thread.kill_server()
    #     self.server_thread = None
    #     log.info("等待60秒后重启")
    #     await asyncio.sleep(60)
    #     self.server_thread = ServerPipeThread(self)

    #     self.rcon.disconnect()

    #     retry_rcon(self)

    # async def check_server_alive(self):
    #     if self.server_thread is None:
    #         return
    #     if self.server_thread.process.poll() is not None and self.server_thread.is_alive():
    #         log.warning("Server closed or crashed, restarting...")
    #         await self.restart_server(0)


def main():
    bot = TofuBot()
    bot.run()
