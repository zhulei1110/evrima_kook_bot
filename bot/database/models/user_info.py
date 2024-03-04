import datetime
from enum import IntEnum
from typing import Dict, Optional

from tortoise import Model, fields

class VipTypes(IntEnum):
    # 无
    NONE = 0
    # 周
    WEEK = 1
    # 月
    MONTH = 2
    # 季度
    QUARTER = 3
    # 年
    YEAR = 4
    # 永久
    PERMANENT = 5

    def to_chinese(self):
        if self == VipTypes.WEEK:
            return '周度'
        if self == VipTypes.MONTH:
            return '月度'
        if self == VipTypes.QUARTER:
            return '季度'
        if self == VipTypes.YEAR:
            return '年度'
        if self == VipTypes.PERMANENT:
            return '永久'
        return None

    def get_egg_everyday(self):
        if self == VipTypes.WEEK:
            return 1
        if self == VipTypes.MONTH:
            return 1
        if self == VipTypes.QUARTER:
            return 1
        if self == VipTypes.YEAR:
            return 2
        if self == VipTypes.PERMANENT:
            return 3
        return 0


class UserInfo(Model):
    # 唯一id
    id: int = fields.IntField(pk=True, generated=True)
    # 用户 KOOK ID
    kook_id: str = fields.CharField(max_length=255, unique=True)
    # 用户 steam 17位 id
    steam_17_id: str = fields.CharField(max_length=17, unique=True)
    # VIP 类型
    vip_type: VipTypes = fields.IntEnumField(VipTypes, default=VipTypes.NONE)
    # VIP 剩余天数
    vip_days: int = fields.IntField(default=0)
    # 龙蛋数量
    dragon_egg: int = fields.IntField(default=0)
    # 龙蛋孵化进度
    dragon_egg_hatch_percent: int = fields.IntField(default=0)
    # 上次孵化龙蛋时间
    last_dragon_egg_hatch_date: datetime.datetime = fields.DatetimeField(null=True)
    # 龙的库存
    dragon_inventory: Dict[str, int] = fields.JSONField(default={})
    # 月卡天数
    monthly_card_days: Optional[int] = fields.IntField(default=0, null=True)
    # 上次月卡孵蛋时间
    last_monthly_card_hatch_date: Optional[datetime.datetime] = fields.DatetimeField(null=True)
    # 注册时间
    create_date: Optional[datetime.datetime] = fields.DatetimeField(null=True)
