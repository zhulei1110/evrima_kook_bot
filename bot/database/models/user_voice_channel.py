from tortoise import Model, fields

class UserVoiceChannel(Model):
    # KOOK 用户 ID
    kook_id: str = fields.CharField(255, unique=True, pk=True)
    # 语音频道 ID
    channel_id: str = fields.CharField(255, unique=True)
