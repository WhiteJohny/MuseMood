import sys

from aiogram.types import Message, CallbackQuery

from src.bot.logic.keyboards import get_playlist_audio_kb, get_playlists_kb
from src.bot.logic.utils import commands
from src.bot.logic.views import get_bot_start_msg, get_bot_stop_msg, get_audio_list_msg, get_playlists_msg
from src.bot.logic.settings import Secrets, logger, set_log
from src.bot.logic.settings import bot


async def bot_start():
    logger.info(set_log('Start bot', special="!!!!!!!!!!!!!Бот запущен!!!!!!!!!!!!!"))
    await commands.set_commands(bot)
    for admin in Secrets.admins_id.split(" "):
        await bot.send_message(chat_id=int(admin), text=get_bot_start_msg())


async def bot_stop():
    logger.info(set_log('Stop bot', special="!!!!!!!!!!!!!Бот остановлен!!!!!!!!!!!!!"))
    for admin in Secrets.admins_id.split(" "):
        await bot.send_message(chat_id=int(admin), text=get_bot_stop_msg())


async def stop_command_handler(message: Message):
    logger.info(set_log('Stop command'), message.message_id, message.from_user.username)
    await bot.session.close()
    try:
        sys.exit()
    except Exception:
        pass


async def playlists_page_handler(callback: CallbackQuery):
    logger.info(set_log('Playlists page handler', callback.message.message_id, callback.from_user.username))
    page_id = int(callback.data.split("_")[2])

    await callback.message.delete()

    # Должен быть запрос к БД для получения плейлистов пользователя
    # playlists = get_user_playlist(message.from_user.id)

    return await callback.message.answer(
        get_playlists_msg(),
        reply_markup=get_playlists_kb(['1', '2', '3'], page_id)
    )
    # get_playlists_kb(playlists)


async def audio_list_handler(callback: CallbackQuery):
    logger.info(set_log('Audio list handler', callback.message.message_id, callback.from_user.username))
    data = callback.data.split("_")
    playlist_id = int(data[2])
    page_id = int(data[4])
    playlist_title = str(playlist_id)  # Запрос к БД get_playlist_title(playlist_id)

    await callback.message.delete()

    return await callback.message.answer(
        get_audio_list_msg(playlist_title),
        reply_markup=get_playlist_audio_kb(playlist_id, page_id)
    )


async def audio_handler(callback: CallbackQuery):
    logger.info(set_log('Audio handler', callback.message.message_id, callback.from_user.username))
    audio_id = int(callback.data.split("_")[1])
    # Нужно придумать функционал (Сообщение пользователя с этим треком/Клавиатура с редактированием названия и
    # удалением трека)
    return await callback.message.answer(str(audio_id))


async def audio_add_handler(callback: CallbackQuery):
    logger.info(set_log('Audio add handler', callback.message.message_id, callback.from_user.username))
    playlist_id = callback.data.split("_")[3]
    # Непонятно как лучше добавить из уже обработанных/загруженных или как новый трек по ссылке/файлу
    return await callback.message.answer(f'Заглушка для добавления аудио {playlist_id}')
