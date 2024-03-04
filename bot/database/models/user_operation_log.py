import datetime
from enum import IntEnum
from typing import Optional

from tortoise import Model, fields

class UserOperationTypes(IntEnum):
    # 无
    NONE = 0
    # 注册用户
    REGISTER_USER = 1
    # 查询库存
    QUERY_INVENTORY = 2
    # 存龙
    SAVE_DINOSAUR = 3
    # 取龙请求
    GET_DINOSAUR_REQUEST = 4
    # 孵化恐龙龙蛋
    HATCHING_DINOSAUR_EGG = 5
    # 购买恐龙（龙蛋换龙）
    BUG_DINOSAUR = 6
    # 购买龙蛋请求
    BUG_DINOSAUR_EGG_REQUEST = 7
    # 购买龙蛋成功
    BUG_DINOSAUR_EGG_SUCCESS = 8
    # 开通会员请求
    JOIN_VIP_REQUEST = 9
    # 开通会员成功
    JOIN_VIP_SUCCESS = 10
    # 开通孵化月卡请求
    JOIN_HATCHING_MONTHLY_CARD_REQUEST = 11
    # 开通孵化月卡成功
    JOIN_HATCHING_MONTHLY_CARD_SUCCESS = 12
    # 成为赞助者请求
    BECOME_SPONSOR_REQUEST = 13
    # 成为赞助者成功
    BECOME_SPONSOR_SUCCESS = 14


class UserOperationLog(Model):
    # 唯一id
    id: int = fields.IntField(pk=True, generated=True)
    # 用户 KOOK ID
    kook_id: str = fields.CharField(max_length=255, null=True)
    # 目标用户 Steam ID
    steam_id: str = fields.CharField(max_length=17, null=True)
    # 操作类型
    operation_type: UserOperationTypes = fields.IntEnumField(UserOperationTypes, default=UserOperationTypes.NONE)
    # 描述
    description: str = fields.CharField(max_length=2048)
    # 创建时间
    create_time: datetime.datetime = fields.DatetimeField(null=True)
