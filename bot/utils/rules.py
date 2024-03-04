from khl import Message

from .config import config


def is_owner(msg: Message) -> bool:
    return msg.author.id == config.owner_id


def is_admin(msg: Message) -> bool:
    return msg.author.id in config.admin_list or msg.author.id == config.owner_id
