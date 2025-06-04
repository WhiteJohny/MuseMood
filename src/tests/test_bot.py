import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

# Исправленные импорты согласно структуре проекта
from src.bot.logic import views, keyboards, fsm
from src.bot.logic.utils import commands
from src.bot.logic.handlers import simple
from src.database import crud, models


# Тесты для views.py
def test_view_messages():
    assert views.get_start_msg("Test") == "Приветствую👋, Test!\nЧтобы узнать, что я умею - напиши\n/help"
    assert views.get_help_msg() == "Функционал бота:"
    assert views.get_menu_msg() == 'Меню'
    assert views.get_profile_msg() == 'Ваш профиль'
    assert views.get_playlists_msg() == 'Ваши плейлисты'
    assert views.get_playlists_error_msg() == 'Не удалось перейти на страницу :('
    assert views.get_bot_start_msg() == "Бот успешно запущен"
    assert views.get_bot_stop_msg() == "Бот завершил работу"
    assert views.get_analysis_msg() == 'Пришлите ссылку или файл с вашим треком'
    assert views.get_garbage_msg() == 'Пропишите /start - чтобы начать!'
    assert views.get_playlist_creation_msg() == 'Введите названия плейлиста'
    assert views.get_error_message() == "Что-то пошло не так :("


# Тесты для keyboards.py
def test_keyboard_creation():
    # Главное меню
    main_kb = keyboards.get_main_menu_kb()
    assert len(main_kb.keyboard) == 1
    assert main_kb.keyboard[0][0].text == "Анализ"
    assert main_kb.keyboard[0][1].text == "Профиль"

    # Меню анализа
    analysis_kb = keyboards.get_analysis_kb()
    assert len(analysis_kb.keyboard) == 1
    assert analysis_kb.keyboard[0][0].text == "Назад"

    # Профиль
    profile_kb = keyboards.get_profile_kb()
    assert len(profile_kb.keyboard) == 2
    assert profile_kb.keyboard[0][0].text == "Плейлисты"
    assert profile_kb.keyboard[0][1].text == "Создать плейлист"

    # Плейлисты
    playlists = [(1, "Playlist1"), (2, "Playlist2")]
    playlists_kb = keyboards.get_playlists_kb(playlists)
    assert len(playlists_kb.inline_keyboard) == 3  # 2 плейлиста + выход


# Тесты для fsm.py
def test_fsm_structure():
    assert fsm.STATES[fsm.User.analysis] == fsm.User.menu
    assert fsm.STATES[fsm.User.profile] == fsm.User.menu
    assert fsm.STATES[fsm.User.creation] == fsm.User.profile

    assert fsm.KEYBOARDS[fsm.User.menu] == keyboards.get_main_menu_kb
    assert fsm.VIEWS[fsm.User.analysis] == views.get_analysis_msg


# Тесты для commands.py
@pytest.mark.asyncio
async def test_set_commands():
    mock_bot = AsyncMock()
    mock_bot.set_my_commands = AsyncMock()

    with patch('src.bot.logic.settings.Secrets', new=MagicMock(admins_id="123 456")):
        await commands.set_commands(mock_bot)

        assert mock_bot.set_my_commands.call_count == 2
        assert len(mock_bot.set_my_commands.call_args_list[0][0][0]) == 2  # Обычные команды
        assert len(mock_bot.set_my_commands.call_args_list[1][0][0]) == 3  # Админские команды


# Тесты для simple.py
# @pytest.mark.asyncio
# async def test_start_handler():
#     mock_message = AsyncMock()
#     mock_message.from_user.id = 123
#     mock_message.from_user.full_name = "Test User"
#     mock_message.from_user.username = "test"
#
#     # Критически важно: добавляем мок для bot
#     mock_message.bot = AsyncMock()
#
#     mock_state = AsyncMock()
#
#     # Настраиваем возвращаемые значения
#     mock_user = MagicMock()
#     mock_user.id = 123
#
#     with patch('src.database.crud.get_user', AsyncMock(return_value=None)), \
#             patch('src.database.crud.create_user', AsyncMock(return_value=mock_user)), \
#             patch('src.database.crud.create_playlist', AsyncMock()):
#         await simple.start_command_handler(mock_message, mock_state)
#
#         mock_message.answer.assert_called_with(
#             views.get_start_msg("Test User"),
#             reply_markup=keyboards.get_main_menu_kb()
#         )
#         mock_state.set_state.assert_called_with(fsm.User.menu)


@pytest.mark.asyncio
async def test_back_handler():
    mock_message = AsyncMock()
    mock_state = AsyncMock()
    mock_state.get_state.return_value = fsm.User.profile

    await simple.back_handler(mock_message, mock_state)
    mock_state.set_state.assert_called_with(fsm.User.menu)
    mock_message.answer.assert_called_with(
        views.get_menu_msg(),
        reply_markup=keyboards.get_main_menu_kb()
    )


@pytest.mark.asyncio
async def test_audio_analysis_handler():
    mock_message = AsyncMock()
    mock_state = AsyncMock()

    await simple.audio_analysis_handler(mock_message, mock_state)
    mock_state.set_state.assert_called_with(fsm.User.analysis)
    mock_message.answer.assert_called_with(
        views.get_analysis_msg(),
        reply_markup=keyboards.get_analysis_kb()
    )


# Тесты для crud.py
@pytest.mark.asyncio
async def test_user_crud():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_user = models.User(id=123, username="test")

    # Create
    await crud.create_user(mock_session, 123, "test")
    mock_session.add.assert_called()
    mock_session.commit.assert_called()

    # Read
    mock_session.get.return_value = mock_user
    user = await crud.get_user(mock_session, 123)
    assert user.id == 123

    # Update
    await crud.update_user(mock_session, 123, new_username="new_test")
    assert mock_session.get.return_value.username == "new_test"

    # Delete
    mock_session.get.return_value = mock_user
    result = await crud.delete_user(mock_session, 123)
    assert result is True
    mock_session.delete.assert_called_with(mock_user)


@pytest.mark.asyncio
async def test_playlist_crud():
    mock_session = AsyncMock(spec=AsyncSession)

    # Create
    await crud.create_playlist(mock_session, "Test", 123)
    mock_session.add.assert_called()
    mock_session.commit.assert_called()

    # Get user playlists
    mock_session.execute.return_value = MagicMock()
    mock_session.execute.return_value.all.return_value = [(1, "Test")]
    playlists = await crud.get_user_playlists(mock_session, 123)
    assert playlists == [(1, "Test")]


# Тесты для моделей
def test_models_structure():
    assert hasattr(models.User, 'playlists')
    assert hasattr(models.Playlist, 'audios')
    assert hasattr(models.Audio, 'playlists')
    assert models.Playlist.__table_args__ is not None
