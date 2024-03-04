import re
from typing import Tuple, Optional

from ...utils.config import config


def get_player_dino_kind(steam_id: str) -> Tuple[Optional[str], Optional[str]]:
    with open(config.game_log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    dino = None
    growth = None
    for line in lines:
        if 'LogTheIsleJoinData' in line:
            if 'Joined The Server' in line and steam_id in line:
                finds = re.findall(r'BP_(.*)_C', line)
                if len(finds) == 0:
                    continue
                dino = finds[0]
                finds = re.findall(r'Growth: (.*)', line)
                if len(finds) == 0:
                    continue
                growth = finds[0]
            elif 'Save file not found' in line and steam_id in line:
                finds = re.findall(r'BP_(.*)_C', line)
                if len(finds) == 0:
                    continue
                dino = finds[0]
                finds = re.findall(r'Growth: (.*)', line)
                if len(finds) == 0:
                    continue
                growth = finds[0]
            elif 'Left The Server' in line and steam_id in line:
                finds = re.findall(r'Was playing as: (.*), Gender', line)
                if len(finds) == 0:
                    continue
                dino = finds[0]
                finds = re.findall(r'Growth: (.*)', line)
                if len(finds) == 0:
                    continue
                growth = finds[0]
    return dino, growth
