import logging
import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from dataclasses import dataclass


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("telegram_bot")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler("bot.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def set_log(action: str, message_id: int = 0, username: str = '', special: str = ''):
    if special:
        return f'Action: {action} - Additional info: {special}'

    return f'Action: {action} - Message id: {message_id} - User: {username}'


logger = setup_logger()
load_dotenv()


@dataclass
class Secrets:
    bot_token: str = os.getenv("BOT_TOKEN")
    admins_id: str = os.getenv("ADMINS_ID")

    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")
    db_name: str = os.getenv("DB_NAME")
    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")


bot = Bot(token=Secrets.bot_token, default=DefaultBotProperties(parse_mode='HTML'))
