import json
import os.path
from typing import Dict, List


class GachaPool:
    weight: int
    dragons: List[str]

    def __init__(self, **kwargs) -> None:
        self.weight = kwargs.get('weight')
        self.dragons = kwargs.get('dragons')


class DragonInfo:
    translate_name: str
    cost: int
    count: int

    def __init__(self, **kwargs) -> None:
        self.translate_name = kwargs.get('translate_name')
        self.cost = kwargs.get('cost')
        self.count = kwargs.get('count')


class Config:
    token: str
    log_level: str
    owner_id: str
    admin_list: List[str]
    guild_id: str
    get_dragon_channel: str
    game_save_path: str
    game_log_path: str
    # server_command: str
    # server_path: str
    rcon_address: str
    rcon_port: int
    rcon_password: str
    rcon_enabled: bool
    timed_announcement: str
    dragon_info: Dict[str, DragonInfo]
    dragon_gacha: List[GachaPool]
    welcome_message: str
    replies: Dict[str, str]
    voice_parent_id: str

    def __init__(self, **kwargs) -> None:
        self.token = kwargs.get('token', '')
        self.log_level = kwargs.get('log_level', 'INFO')
        self.owner_id = kwargs.get('owner_id', '')
        self.admin_list = kwargs.get('admin_list', [])
        self.guild_id = kwargs.get('guild_id', '')
        self.voice_parent_id = kwargs.get('voice_parent_id', '')
        self.get_dragon_channel = kwargs.get('get_dragon_channel', '')
        # self.server_command = kwargs.get('server_command', '')
        # self.server_path = kwargs.get('server_path', '')
        self.game_save_path = kwargs.get('game_save_path', '')
        self.game_log_path = kwargs.get('game_log_path', '')
        self.rcon_address = kwargs.get('rcon_address', '127.0.0.1')
        self.rcon_port = kwargs.get('rcon_port', 8888)
        self.rcon_password = kwargs.get('rcon_password', '')
        self.rcon_enabled = kwargs.get('rcon_enabled', False)
        self.timed_announcement = kwargs.get('timed_announcement', '')
        self.welcome_message = kwargs.get('welcome_message', '')
        self.replies = kwargs.get('replies', {})

        _dragon_info = kwargs.get('dragon_info', {})
        self.dragon_info = {}
        for name in _dragon_info:
            info = _dragon_info[name]
            self.dragon_info[name] = DragonInfo(**info)

        _dragon_gacha = kwargs.get('dragon_gacha', [])
        self.dragon_gacha = []
        for pool in _dragon_gacha:
            self.dragon_gacha.append(GachaPool(**pool))

    @classmethod
    def load(cls):
        if not os.path.exists('config.json'):
            return cls()
        with open('config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

    def save(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.dict, f, indent=4, ensure_ascii=False)

    @property
    def dict(self):
        _dragon_info = {}
        for name in self.dragon_info:
            info = self.dragon_info[name]
            _dragon_info[name] = {
                'translate_name': info.translate_name,
                'cost': info.cost,
                'count': info.count
            }

        _dragon_gacha = []
        for pool in self.dragon_gacha:
            _dragon_gacha.append({
                'weight': pool.weight,
                'dragons': pool.dragons
            })
        return {
            'token': self.token,
            'log_level': self.log_level,
            'owner_id': self.owner_id,
            'admin_list': self.admin_list,
            'guild_id': self.guild_id,
            'voice_parent_id': self.voice_parent_id,
            'get_dragon_channel': self.get_dragon_channel,
            'game_save_path': self.game_save_path,
            'game_log_path': self.game_log_path,
            # 'server_command': self.server_command,
            # 'server_path': self.server_path,
            'rcon_address': self.rcon_address,
            'rcon_port': self.rcon_port,
            'rcon_password': self.rcon_password,
            'rcon_enabled': self.rcon_enabled,
            'timed_announcement': self.timed_announcement,
            'welcome_message': self.welcome_message,
            'replies': self.replies,
            'dragon_info': _dragon_info,
            'dragon_gacha': _dragon_gacha
        }


config = Config.load()
config.save()
