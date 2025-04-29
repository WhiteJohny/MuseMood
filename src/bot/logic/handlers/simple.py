from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from random import choice

from src.bot.logic.settings import logger, set_log
from src.bot.logic.keyboards import get_main_menu_kb, get_analysis_kb, get_profile_kb, get_playlists_kb, \
    get_create_playlist_kb
from src.bot.logic.fsm import User, STATES, KEYBOARDS, VIEWS
from src.bot.logic.utils.audio_converters import get_audio_sentiments
from src.bot.logic.utils.audio_parsers import download_yt_audio, download_tg_audio
from src.bot.logic.views import get_start_msg, get_help_msg, get_model_msg, get_model_error, get_analysis_msg, \
    get_garbage_msg, get_profile_msg, get_playlists_msg, get_playlist_creation_msg, get_playlist_creation_title_msg

SENTIMENTS = ['funny', 'happy', 'sad', 'scary', 'tender', 'trance', None]


async def garbage_handler(message: Message, state: FSMContext):
    logger.info(set_log('Garbage handler', message.message_id, message.from_user.username))
    curr_state = await state.get_state()
    if not curr_state:
        return await message.answer(get_garbage_msg())


async def start_command_handler(message: Message, state: FSMContext):
    logger.info(set_log('Start command', message.message_id, message.from_user.username))
    await state.set_state(User.menu)
    return await message.answer(get_start_msg(message.from_user.full_name), reply_markup=get_main_menu_kb())


async def help_command_handler(message: Message):
    logger.info(set_log('Help command', message.message_id, message.from_user.username))
    return await message.answer(get_help_msg())


async def audio_analysis_handler(message: Message, state: FSMContext):
    logger.info(set_log('Track analysis handler', message.message_id, message.from_user.username))
    await state.set_state(User.analysis)
    return await message.answer(get_analysis_msg(), reply_markup=get_analysis_kb())


async def audio_analysis_link_handler(message: Message):
    logger.info(set_log('Track analysis process link', message.message_id, message.from_user.username))
    if message.text.startswith('https://www.youtube.com/'):
        audio_path, duration = await download_yt_audio(message.text)
        if audio_path and duration > 0:
            audio_sentiments = get_audio_sentiments(audio_path, duration=duration)
            if audio_sentiments:
                model_res = choice(SENTIMENTS)  # Для имитации работы модели -> get_sentiments(audio_sentiments)

                if model_res:
                    return await message.reply(get_model_msg(audio_path), reply_markup=get_analysis_kb())

    return await message.answer(get_model_error(), reply_markup=get_analysis_kb())


async def audio_analysis_file_handler(message: Message):
    logger.info(set_log('Track analysis process file', message.message_id, message.from_user.username))
    audio_path = await download_tg_audio(message)
    if audio_path:
        audio_sentiments = get_audio_sentiments(audio_path, duration=message.audio.duration)
        if audio_sentiments:
            model_res = choice(SENTIMENTS)  # Для имитации работы модели -> get_sentiments(audio_sentiments)

            if model_res:
                return await message.reply(get_model_msg(audio_path), reply_markup=get_analysis_kb())

    return await message.answer(get_model_error(), reply_markup=get_analysis_kb())


async def back_handler(message: Message, state: FSMContext):
    logger.info(set_log('Back handler', message.message_id, message.from_user.username))
    curr_state = await state.get_state()
    prev_state = STATES.get(curr_state)
    if prev_state:
        await state.set_state(prev_state)
        return await message.answer(VIEWS.get(prev_state)(), reply_markup=KEYBOARDS.get(prev_state)())


async def profile_handler(message: Message, state: FSMContext):
    logger.info(set_log('Profile handler', message.message_id, message.from_user.username))
    await state.set_state(User.profile)
    return await message.answer(get_profile_msg(), reply_markup=get_profile_kb())


async def playlists_handler(message: Message):
    logger.info(set_log('Playlists handler', message.message_id, message.from_user.username))
    # Должен быть запрос к БД для получения плейлистов пользователя
    # playlists = get_user_playlist(message.from_user.id)
    return await message.answer(get_playlists_msg(), reply_markup=get_playlists_kb(['1', '2', '3']))
    # get_playlists_kb(playlists)


async def playlist_creation_handler(message: Message, state: FSMContext):
    logger.info(set_log('Playlist creation handler', message.message_id, message.from_user.username))
    await state.set_state(User.creation)
    return await message.answer(get_playlist_creation_msg(), reply_markup=get_create_playlist_kb())


async def playlist_creation_title_handler(message: Message, state: FSMContext):
    logger.info(set_log('Playlist creation title handler', message.message_id, message.from_user.username))
    # тут функция добавления плейлиста в БД
    error_flag = False
    if error_flag:
        return await message.answer(get_playlist_creation_title_msg(error_flag), reply_markup=get_create_playlist_kb())

    await state.set_state(User.profile)
    return await message.answer(get_playlist_creation_title_msg(error_flag), reply_markup=get_profile_kb())
