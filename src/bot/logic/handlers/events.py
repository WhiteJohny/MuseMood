import sys

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError

from src.bot.logic.keyboards import get_playlist_audio_kb, get_playlists_kb, get_add_to_playlist_kb, get_audio_kb, \
    get_approve_kb, get_profile_kb
from src.bot.logic.utils import commands
from src.bot.logic.views import get_bot_start_msg, get_bot_stop_msg, get_audio_list_msg, get_playlists_msg, \
    get_playlists_error_msg, get_error_message, get_model_msg
from src.bot.logic.settings import Secrets, logger, set_log
from src.bot.logic.settings import bot
from src.database.crud import get_user_playlists, get_audios_in_playlist, get_playlist_title, add_audio_to_playlist, \
    get_user_playlist, get_audio, remove_audio_from_playlist, remove_audio, delete_playlist
from src.database.models import async_session_local


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
    except Exception as e:
        print(e)


async def playlists_page_handler(callback: CallbackQuery):
    logger.info(set_log('Playlists page handler', callback.message.message_id, callback.from_user.username))
    page_id = int(callback.data.split("_")[2])

    try:
        async with async_session_local() as session:
            playlists = await get_user_playlists(session, callback.from_user.id)

        await callback.message.delete()

        return await callback.message.answer(
            get_playlists_msg(),
            reply_markup=get_playlists_kb(playlists, page_id)
        )
    except Exception as e:
        logger.info(set_log('Playlists page handler', special=f"ERROR {e}"))
        return await callback.message.answer(get_playlists_error_msg())


async def audio_list_handler(callback: CallbackQuery):
    logger.info(set_log('Audio list handler', callback.message.message_id, callback.from_user.username))
    data = callback.data.split("_")
    playlist_id = int(data[2])
    page_id = int(data[4])

    try:
        async with async_session_local() as session:
            playlist_title = await get_playlist_title(session, playlist_id)
            audio_list = await get_audios_in_playlist(session, playlist_id)

        await callback.message.delete()

        flag = True
        if playlist_title == 'All':
            flag = False

        return await callback.message.answer(
            get_audio_list_msg(playlist_title),
            reply_markup=get_playlist_audio_kb(audio_list, playlist_id, page_id, flag=flag)
        )
    except Exception as e:
        logger.info(set_log('Audio list handler', special=f"ERROR {e}"))
        return await callback.message.answer(get_error_message())


async def audio_handler(callback: CallbackQuery):
    logger.info(set_log('Audio handler', callback.message.message_id, callback.from_user.username))
    data = callback.data.split("_")
    audio_id = int(data[1])
    playlist_id = int(data[3])
    page = int(data[5])

    try:
        async with async_session_local() as session:
            audio = await get_audio(session, audio_id)

        try:
            await callback.message.answer(
                get_model_msg(audio),
                reply_to_message_id=audio.message_id,
                reply_markup=get_audio_kb(audio_id, playlist_id, page)
            )
            await callback.message.delete()
        except TelegramBadRequest:
            async with async_session_local() as session:
                await remove_audio(session, audio_id)
            return callback.message.answer("Сообщение не найдено")

    except Exception as e:
        logger.info(set_log('Audio handler', special=f"ERROR {e}"))
        return callback.message.answer(get_error_message())


async def audio_page_handler(callback: CallbackQuery):
    logger.info(set_log('Audio page handler', callback.message.message_id, callback.from_user.username))
    data = callback.data.split("_")
    page_id = int(data[4])
    playlist_id = int(data[6])

    try:
        async with async_session_local() as session:
            all_id = await get_user_playlist(session, callback.from_user.id)
            audio_list = await get_audios_in_playlist(session, all_id)

        await callback.message.delete()

        return await callback.message.answer(
            'Ваши аудио',
            reply_markup=get_add_to_playlist_kb(audio_list, playlist_id, page_id)
        )
    except Exception as e:
        logger.info(set_log('Audio page handler', special=f"ERROR {e}"))
        return callback.message.answer(get_error_message())


async def audio_add_handler(callback: CallbackQuery):
    logger.info(set_log('Audio add handler', callback.message.message_id, callback.from_user.username))
    data = callback.data.split("_")
    audio_id = int(data[2])
    playlist_id = int(data[4])

    try:
        try:
            async with async_session_local() as session:
                await add_audio_to_playlist(session, playlist_id, audio_id)
        except IntegrityError:
            return callback.message.answer('Трек уже в плейлисте!')
    except Exception as e:
        logger.info(set_log('Audio add handler', special=f"ERROR {e}"))
        return callback.message.answer(get_error_message())

    return callback.message.answer('Трек успешно добавлен!')


async def exit_to_menu_handler(callback: CallbackQuery):
    logger.info(set_log('Exit to menu handler', callback.message.message_id, callback.from_user.username))
    await callback.message.delete()


async def audio_delete_handler(callback: CallbackQuery):
    logger.info(set_log('Audio delete handler', callback.message.message_id, callback.from_user.username))
    data = callback.data.split("_")
    audio_id = int(data[2])
    playlist_id = int(data[4])
    page = int(data[6])

    try:
        flag = True
        async with async_session_local() as session:
            playlist_title = await get_playlist_title(session, playlist_id)
            if playlist_title == 'All':
                flag = False
                await remove_audio(session, audio_id)
            else:
                await remove_audio_from_playlist(session, playlist_id, audio_id)
            audio_list = await get_audios_in_playlist(session, playlist_id)
    except Exception as e:
        logger.info(set_log('Audio add handler', special=f"ERROR {e}"))
        return callback.message.answer(get_error_message())

    await callback.message.delete()

    return callback.message.answer(
        'Трек успешно удален!',
        reply_markup=get_playlist_audio_kb(audio_list, playlist_id, page, flag)
    )


async def playlist_delete_approve_handler(callback: CallbackQuery):
    logger.info(set_log('Playlist delete approve handler', callback.message.message_id, callback.from_user.username))
    data = callback.data.split("_")
    playlist_id = int(data[3])
    page = int(data[5])

    try:
        async with async_session_local() as session:
            playlist_title = await get_playlist_title(session, playlist_id)
    except Exception as e:
        logger.info(set_log('Playlist delete approve handler', special=f"ERROR {e}"))
        return callback.message.answer(get_error_message())

    await callback.message.delete()

    return await callback.message.answer(
        f'Вы уверены, что хотите удалить {playlist_title}?',
        reply_markup=get_approve_kb(playlist_id, page)
    )


async def playlist_delete_handler(callback: CallbackQuery):
    logger.info(set_log('Playlist delete handler', callback.message.message_id, callback.from_user.username))
    playlist_id = int(callback.data.split("_")[2])

    try:
        async with async_session_local() as session:
            await delete_playlist(session, playlist_id)
    except Exception as e:
        logger.info(set_log('Playlist delete handler', special=f"ERROR {e}"))
        return callback.message.answer(get_error_message())

    await callback.message.delete()

    return await callback.message.answer("Плейлист удален!", reply_markup=get_profile_kb())
