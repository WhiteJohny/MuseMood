import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.model.evaluate import load_model, evaluate_mood
from src.database.models import async_session_local
from src.database.crud import get_user, create_user, create_playlist, create_audio, get_user_playlist, \
    add_audio_to_playlist, get_user_playlists

from src.bot.logic.settings import logger, set_log, Secrets
from src.bot.logic.keyboards import get_main_menu_kb, get_analysis_kb, get_profile_kb, get_playlists_kb, \
    get_create_playlist_kb
from src.bot.logic.fsm import User, STATES, KEYBOARDS, VIEWS
from src.bot.logic.utils.audio_converters import get_audio_sentiments
from src.bot.logic.utils.audio_parsers import download_yt_audio, download_tg_audio
from src.bot.logic.views import get_start_msg, get_help_msg, get_model_msg, get_model_error, get_analysis_msg, \
    get_garbage_msg, get_profile_msg, get_playlists_msg, get_playlist_creation_msg, get_playlist_creation_title_msg, \
    get_error_message

model = load_model(Secrets.model_name)


async def garbage_handler(message: Message, state: FSMContext):
    logger.info(set_log('Garbage handler', message.message_id, message.from_user.username))
    curr_state = await state.get_state()
    if not curr_state:
        return await message.answer(get_garbage_msg())


async def start_command_handler(message: Message, state: FSMContext):
    logger.info(set_log('Start command', message.message_id, message.from_user.username))

    try:
        async with async_session_local() as session:
            user = await get_user(session, message.from_user.id)
            if not user:
                await create_user(session, message.from_user.id, message.from_user.username)
                await create_playlist(session, 'All', message.from_user.id)

        await state.set_state(User.menu)

        return await message.answer(get_start_msg(message.from_user.full_name), reply_markup=get_main_menu_kb())
    except Exception as e:
        logger.info(set_log('Start command handler', special=f"ERROR {e}"))
        return await message.answer(get_error_message())


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
        audio_path, duration = await asyncio.to_thread(
            download_yt_audio,
            message.text
        )
        if audio_path and duration > 0:
            audio_sentiments = await asyncio.to_thread(
                get_audio_sentiments,
                audio_path,
                duration
            )
            if audio_sentiments:
                model_res = await asyncio.to_thread(
                    evaluate_mood,
                    model,
                    audio_sentiments
                )
                if '1' in model_res:
                    try:
                        async with async_session_local() as session:
                            audio = await create_audio(
                                session,
                                audio_path[13:],
                                message.message_id,
                                model_res,
                                link=message.text
                            )
                            playlist_id = await get_user_playlist(session, message.from_user.id)
                            await add_audio_to_playlist(session, playlist_id, audio.id)
                        return await message.reply(get_model_msg(audio), reply_markup=get_analysis_kb())
                    except Exception as e:
                        logger.info(set_log('Track analysis process link', special=f"ERROR {e}"))
    return await message.answer(get_model_error(), reply_markup=get_analysis_kb())


async def audio_analysis_file_handler(message: Message):
    logger.info(set_log('Track analysis process file', message.message_id, message.from_user.username))
    audio_path = await download_tg_audio(message)
    if audio_path:
        audio_sentiments = await asyncio.to_thread(
            get_audio_sentiments,
            audio_path,
            message.audio.duration
        )
        if audio_sentiments:
            model_res = await asyncio.to_thread(
                evaluate_mood,
                model,
                audio_sentiments
            )

            if '1' in model_res:
                try:
                    async with async_session_local() as session:
                        audio = await create_audio(
                            session,
                            audio_path[13:],
                            message.message_id,
                            model_res,
                            file_id=message.audio.file_id
                        )
                        playlist_id = await get_user_playlist(session, message.from_user.id)
                        await add_audio_to_playlist(session, playlist_id, audio.id)
                    return await message.reply(get_model_msg(audio), reply_markup=get_analysis_kb())
                except Exception as e:
                    logger.info(set_log('Track analysis process file', special=f"ERROR {e}"))
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
    async with async_session_local() as session:
        playlists = await get_user_playlists(session, message.from_user.id)
    return await message.answer(get_playlists_msg(), reply_markup=get_playlists_kb(playlists))


async def playlist_creation_handler(message: Message, state: FSMContext):
    logger.info(set_log('Playlist creation handler', message.message_id, message.from_user.username))
    await state.set_state(User.creation)
    return await message.answer(get_playlist_creation_msg(), reply_markup=get_create_playlist_kb())


async def playlist_creation_title_handler(message: Message, state: FSMContext):
    logger.info(set_log('Playlist creation title handler', message.message_id, message.from_user.username))
    async with async_session_local() as session:
        playlist = await create_playlist(session, message.text, message.from_user.id)

    if not playlist:
        return await message.answer(get_playlist_creation_title_msg(True), reply_markup=get_create_playlist_kb())

    await state.set_state(User.profile)
    return await message.answer(get_playlist_creation_title_msg(False), reply_markup=get_profile_kb())


async def cancel_playlist_creation_handler(message: Message, state: FSMContext):
    logger.info(set_log('cancel playlist creation handler', message.message_id, message.from_user.username))
    await state.set_state(User.profile)
    return await message.answer(get_profile_msg(), reply_markup=get_profile_kb())
