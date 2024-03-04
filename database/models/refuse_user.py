from tortoise import Model, fields

class RefuseUser(Model):
    id: int = fields.IntField(pk=True, generated=True)
    # 被拒绝的 KOOK 用户 ID
    kook_id: str = fields.CharField(255, unique=True)
