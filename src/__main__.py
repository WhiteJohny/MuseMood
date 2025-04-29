import asyncio

from aiogram import Dispatcher, F

from aiogram.filters import Command, StateFilter
from aiogram.methods import DeleteWebhook

from src.bot.logic.handlers.simple import start_command_handler, help_command_handler, audio_analysis_handler, \
    audio_analysis_link_handler, audio_analysis_file_handler, garbage_handler, back_handler, profile_handler, \
    playlists_handler, playlist_creation_handler, playlist_creation_title_handler

from src.bot.logic.handlers.events import bot_start, bot_stop, stop_command_handler, audio_list_handler, \
    audio_handler, playlists_page_handler, audio_add_handler

from src.bot.logic.settings import bot

from src.bot.logic.fsm import User


async def start():
    dp = Dispatcher()

    dp.startup.register(bot_start)
    dp.shutdown.register(bot_stop)

    dp.message.register(start_command_handler, Command(commands='start'))
    dp.message.register(help_command_handler, Command(commands='help'))
    dp.message.register(stop_command_handler, Command(commands='stop'))

    dp.callback_query.register(playlists_page_handler, F.data.startswith("playlist_page_"))
    dp.callback_query.register(audio_list_handler, F.data.startswith("playlist_audio_"))
    dp.callback_query.register(audio_handler, F.data.startswith("audio_"))
    dp.callback_query.register(audio_add_handler, F.data.startswith("add_to_playlist_"))

    dp.message.register(back_handler, F.text == 'Назад')
    dp.message.register(audio_analysis_handler, F.text == 'Анализ', StateFilter(User.menu))
    dp.message.register(profile_handler, F.text == 'Профиль', StateFilter(User.menu))
    dp.message.register(audio_analysis_link_handler, F.text, StateFilter(User.analysis))
    dp.message.register(audio_analysis_file_handler, F.audio, StateFilter(User.analysis))
    dp.message.register(playlists_handler, F.text == 'Плейлисты', StateFilter(User.profile))
    dp.message.register(playlist_creation_handler, F.text == 'Создать плейлист', StateFilter(User.profile))
    dp.message.register(playlist_creation_title_handler, StateFilter(User.creation))

    dp.message.register(garbage_handler)

    try:
        await bot(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
