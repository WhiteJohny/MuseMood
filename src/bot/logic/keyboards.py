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


def get_playlists_kb(playlists: list, page: int = 0, page_size: int = 5):
    builder = InlineKeyboardBuilder()

    start_idx = page * page_size
    end_idx = start_idx + page_size
    paginated_playlists = playlists[start_idx:end_idx]

    for playlist in paginated_playlists:
        builder.row(InlineKeyboardButton(
            text=playlist[1],
            callback_data=f"playlist_audio_{int(playlist[0])}_page_{0}"
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

    builder.row(
        InlineKeyboardButton(
            text='Выход',
            callback_data='exit_to_menu'
        ),
    )

    return builder.as_markup()


def get_playlist_audio_kb(audio_list: list, playlist_id: int, page: int = 0, page_size: int = 5, flag: bool = True):
    builder = InlineKeyboardBuilder()

    start_idx = page * page_size
    end_idx = start_idx + page_size

    paginated_audio = audio_list[start_idx:end_idx]

    for audio in paginated_audio:
        builder.row(InlineKeyboardButton(
            text=f"{audio.title}",
            callback_data=f"audio_{audio.id}_playlist_{playlist_id}_page_{page}"
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
            text="🔙 Назад",
            callback_data=f"playlist_page_{0}"
        ),
        InlineKeyboardButton(
            text="Добавить аудио",
            callback_data=f"add_to_playlist_page_{0}_audio_{playlist_id}"
        )
    )

    if flag:
        builder.row(
            InlineKeyboardButton(
                text='Удалить',
                callback_data=f'delete_approve_playlist_{playlist_id}_page_{page}'
            )
        )

    return builder.as_markup()


def get_add_to_playlist_kb(audio_list: list, playlist_id: int, page: int = 0, page_size: int = 5):
    builder = InlineKeyboardBuilder()

    start_idx = page * page_size
    end_idx = start_idx + page_size
    paginated_audio = audio_list[start_idx:end_idx]

    for audio in paginated_audio:
        builder.row(InlineKeyboardButton(
            text=audio.title,
            callback_data=f"add_audio_{audio.id}_to_{playlist_id}"
        ))

    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"add_to_playlist_page_{page - 1}_audio_{playlist_id}"
        ))
    if end_idx < len(audio_list):
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"add_to_playlist_page_{page + 1}_audio_{playlist_id}"
        ))

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data=f"playlist_audio_{playlist_id}_page_{0}"
    ))

    return builder.as_markup()


def get_create_playlist_kb():
    buttons = [
        [KeyboardButton(text="Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_audio_kb(audio_id: int, playlist_id: int, page: int):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"playlist_audio_{playlist_id}_page_{page}"
        ),
        InlineKeyboardButton(
            text="Удалить",
            callback_data=f"delete_audio_{audio_id}_playlist_{playlist_id}_page_{page}"
        )
    )

    return builder.as_markup()


def get_approve_kb(playlist_id: int, page: int):
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=f"playlist_audio_{playlist_id}_page_{page}"
        ),
        InlineKeyboardButton(
            text="Удалить",
            callback_data=f"delete_playlist_{playlist_id}"
        )
    )

    return builder.as_markup()
