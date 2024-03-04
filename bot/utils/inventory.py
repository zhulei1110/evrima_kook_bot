from .config import config


def get_default_inventory():
    rt = {}
    for name in config.dragon_info:
        rt[name] = 0
    return rt
