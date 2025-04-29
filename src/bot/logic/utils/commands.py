from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from src.bot.logic.settings import Secrets, logger


async def set_commands(bot: Bot):
    bot_commands = [
        BotCommand(
            command='start',
            description='Начало работы'
        ),
        BotCommand(
            command='help',
            description='Что умеет бот'
        ),
    ]
    bot_admin_commands = [
        BotCommand(
            command='stop',
            description='Прекращение работы бота'
        ),
    ]
    bot_admin_commands.extend(bot_commands)

    await bot.set_my_commands(bot_commands, BotCommandScopeDefault())

    for admin in Secrets.admins_id.split(" "):
        try:
            await bot.set_my_commands(bot_admin_commands, BotCommandScopeChat(chat_id=int(admin)))
        except Exception as e:
            logger.info(f'ERROR {e}')
            print(e)
