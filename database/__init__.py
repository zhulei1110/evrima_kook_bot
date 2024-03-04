import logging
from pathlib import Path

from tortoise import Tortoise

log = logging.getLogger(__name__)

DATABASE_PATH = Path() / 'database'
DATABASE_PATH.mkdir(parents=True, exist_ok=True)

USER_DB_PATH = DATABASE_PATH / 'tofu.db'

DATA_BASE = {
    "connections": {
        # "tofu": {
        #     "engine": "tortoise.backends.sqlite",
        #     "credentials": {
        #         "file_path": USER_DB_PATH
        #     }
        # }
        "tofu": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "database": "evrima_kook_bot",
                "user": "",
                "password": "",
                "host": "",
                "port": "3306",
            }
        }
    },
    "apps": {
        "tofu": {
            "models": [
                "bot.database.models.user_info",
                "bot.database.models.refuse_user",
                "bot.database.models.user_voice_channel",
                "bot.database.models.user_operation_log",
                "bot.database.models.admin_operation_log"
            ],
            "default_connection": "tofu"
        }
    }
}


async def connect():
    try:
        await Tortoise.init(config=DATA_BASE)
        await Tortoise.generate_schemas()
        log.info("Connected to database")
    except Exception as e:
        log.error(f"Error connecting to database: ", e)


async def disconnect():
    await Tortoise.close_connections()
    log.info("Disconnected from database")
