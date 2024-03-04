import datetime
from enum import IntEnum
from typing import Dict, Optional

from tortoise import Model, fields

class AdminOperationTypes(IntEnum):
    # 无
    NONE = 0
    # 添加恐龙库存
    ADD_DINOSAUR_INVENTORY = 1
    # 添加恐龙龙蛋
    ADD_DINOSAUR_EGG = 2
    # 更换 Steam ID - 换绑
    CHANGE_STEAM_ID = 3
    # 禁用 Steam 用户 - BAN
    BAN_STEAM_USER = 4
    # 拒绝 kook 用户使用机器人
    REFUSE_KOOK_USER = 5
    # 恢复 kook 用户使用机器人
    RESTORE_KOOK_USER = 6
    # 开通孵化月卡
    JOIN_HATCHING_MONTHLY_CARD = 7
    # 开通会员
    JOIN_VIP = 8


class AdminOperationLog(Model):
    # 唯一id
    id: int = fields.IntField(pk=True, generated=True)
    # 管理员 KOOK ID - 操作人
    admin_kook_id: str = fields.CharField(max_length=255, null=True)
    # 目标用户 KOOK ID
    target_kook_id: str = fields.CharField(max_length=255, null=True)
    # 目标用户 Steam ID
    target_steam_id: Optional[str] = fields.CharField(max_length=17, null=True)
    # 操作类型
    operation_type: AdminOperationTypes = fields.IntEnumField(AdminOperationTypes, default=AdminOperationTypes.NONE)
    # 描述
    description: str = fields.CharField(max_length=2048)
    # 创建时间
    create_time: datetime.datetime = fields.DatetimeField(null=True)
