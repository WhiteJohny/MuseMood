from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_kb():
    buttons = [
        [
            KeyboardButton(text="Анализ"),
            KeyboardButton(text="Профиль")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_analysis_kb():
    buttons = [
        [KeyboardButton(text="Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_profile_kb():
    buttons = [
        [
            KeyboardButton(text="Плейлисты"),
            KeyboardButton(text="Создать плейлист")
         ],
        [KeyboardButton(text="Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_playlists_kb(playlists: list, page: int = 0, page_size: int = 1):
    builder = InlineKeyboardBuilder()

    start_idx = page * page_size
    end_idx = start_idx + page_size
    paginated_playlists = playlists[start_idx:end_idx]

    for playlist in paginated_playlists:
        builder.row(InlineKeyboardButton(
            text=playlist,
            callback_data=f"playlist_audio_{int(playlist)}_page_{0}"
        ))

    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"playlist_page_{page - 1}"
        ))
    if end_idx < len(playlists):
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"playlist_page_{page + 1}"
        ))

    if pagination_buttons:
        builder.row(*pagination_buttons)

    return builder.as_markup()


def get_playlist_audio_kb(playlist_id: int, page: int = 0, page_size: int = 1):
    builder = InlineKeyboardBuilder()

    start_idx = page * page_size
    end_idx = start_idx + page_size
    audio_list = [
        {'id': 1, 'title': 'Bombordiro crocodilo'},
        {'id': 2, 'title': 'Tung tung sakhur'},
        {'id': 3, 'title': 'Tralalelo tralala'}
    ]
    paginated_audio = audio_list[start_idx:end_idx]

    for audio in paginated_audio:
        builder.row(InlineKeyboardButton(
            text=f"{audio['title']}",
            callback_data=f"audio_{audio['id']}"
        ))

    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"playlist_audio_{playlist_id}_page_{page - 1}"
        ))
    if end_idx < len(audio_list):
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"playlist_audio_{playlist_id}_page_{page + 1}"
        ))

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text="Добавить аудио",
            callback_data=f"add_to_playlist_{playlist_id}"
        )
    )

    return builder.as_markup()


# def get_add_to_playlist_kb(playlists: list, audio_id: int, page: int = 0, page_size: int = 1):
#     builder = InlineKeyboardBuilder()
#
#     start_idx = page * page_size
#     end_idx = start_idx + page_size
#     paginated_playlists = playlists[start_idx:end_idx]
#
#     for playlist in paginated_playlists:
#         builder.row(InlineKeyboardButton(
#             text=playlist['name'],
#             callback_data=f"add_audio_{audio_id}_to_{playlist['id']}"
#         ))
#
#     pagination_buttons = []
#     if page > 0:
#         pagination_buttons.append(InlineKeyboardButton(
#             text="⬅️ Назад",
#             callback_data=f"add_to_playlist_page_{page - 1}_audio_{audio_id}"
#         ))
#     if end_idx < len(playlists):
#         pagination_buttons.append(InlineKeyboardButton(
#             text="Вперед ➡️",
#             callback_data=f"add_to_playlist_page_{page + 1}_audio_{audio_id}"
#         ))
#
#     if pagination_buttons:
#         builder.row(*pagination_buttons)
#
#     builder.row(InlineKeyboardButton(
#         text="🔙 Назад",
#         callback_data=f"back_to_playlist_audio"
#     ))
#
#     return builder.as_markup()


def get_create_playlist_kb():
    buttons = [
        [KeyboardButton(text="Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
