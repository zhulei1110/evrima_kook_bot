import logging
import socket
from enum import Enum
from threading import RLock
from typing import Optional


log = logging.getLogger(__name__)


class PacketTypes(Enum):
    EMPTY = '\x00'.encode('utf-8')
    RCON_AUTH = '\x01'.encode('utf-8')
    RCON_EXECCOMMAND = '\x02'.encode('utf-8')
    RCON_RESPONSE_VALUE = '\x03'.encode('utf-8')

    RCON_ANNOUNCE = '\x10'.encode('utf-8')
    RCON_UPDATEPLAYABLES = '\x15'.encode('utf-8')
    RCON_BANPLAYER = '\x20'.encode('utf-8')
    RCON_KICKPLAYER = '\x30'.encode('utf-8')
    RCON_GETPLAYERLIST = '\x40'.encode('utf-8')
    RCON_SAVE = '\x50'.encode('utf-8')
    RCON_COMMAND = '\x70'.encode('utf-8')


class RconConnection:
    BUFFER_SIZE = 2 ** 10
    socket: Optional[socket.socket]

    def __init__(self, address: str, port: int, password: str) -> None:
        self.address = address
        self.port = port
        self.password = password
        self.socket = None
        self.command_lock = RLock()

    def __send(self, payload):
        if self.socket is not None:
            self.socket.send(payload)
        else:
            log.warning('RCON not connected.')

    def __recv(self, __bufsize: int):
        if self.socket is not None:
            return self.socket.recv(__bufsize)
        else:
            log.warning('RCON not connected.')
            return bytes()

    def connect(self) -> bool:
        if self.socket is not None:
            try:
                self.disconnect()
            except Exception:
                pass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.address, self.port))

        self.__send(PacketTypes.RCON_AUTH.value + self.password.encode() + PacketTypes.EMPTY.value)

        message = self.__recv(1024)
        if 'Accepted' in message.decode():
            return True
        else:
            self.disconnect()
            return False

    def disconnect(self):
        """
        Disconnect from the server
        """
        if self.socket is None:
            return
        self.socket.close()
        self.socket = None

    @property
    def connected(self):
        return self.socket is not None

    def announce(self, text: str):
        log.debug(f'RCON send announce: {text}')
        try:
            self.__send(
                PacketTypes.RCON_EXECCOMMAND.value + PacketTypes.RCON_ANNOUNCE.value +
                text.encode() +
                PacketTypes.EMPTY.value
            )
        except ConnectionResetError:
            self.disconnect()

    # def kick_player(self, player_id: str):
    #     self.__send(
    #         PacketTypes.RCON_EXECCOMMAND.value + PacketTypes.RCON_KICKPLAYER.value +
    #         player_id.encode() +
    #         PacketTypes.EMPTY.value
    #     )

    def ban_player(self, steam_id: str, description: str, time: int = 0):
        log.debug(f'RCON ban {steam_id} with description \"{description}\" {time} hours.')
        try:
            self.__send(
                PacketTypes.RCON_EXECCOMMAND.value + PacketTypes.RCON_BANPLAYER.value +
                f'{steam_id},{description},{time}'.encode() +
                PacketTypes.EMPTY.value
            )
        except ConnectionResetError:
            self.disconnect()

    def player_list(self):
        try:
            self.__send(
                PacketTypes.RCON_EXECCOMMAND.value + PacketTypes.RCON_GETPLAYERLIST.value + PacketTypes.EMPTY.value
            )
        except ConnectionResetError:
            self.disconnect()
            return
        msg = self.__recv(2 ** 20)
        if not msg:
            return
        player_list_msg = msg.decode()
        sp = player_list_msg.split('\n')
        id_list = sp[1].split(',')
        return id_list[:-1]

    def save_game(self):
        try:
            self.__send(
                PacketTypes.RCON_EXECCOMMAND.value + PacketTypes.RCON_SAVE.value + PacketTypes.EMPTY.value
            )
        except ConnectionResetError:
            self.disconnect()


# if __name__ == '__main__':
#     rcon = RconConnection('202.189.9.241', 8888, 'hoolordboo5080')
#     # print('Login success? ', rcon.connect())
#     # rcon.announce('Test Announce!!!!!!!')
#     rcon.player_list()
#     # rcon.kick_player('0002494d5bc14607a6c54f77573f3c22')
#     rcon.disconnect()
