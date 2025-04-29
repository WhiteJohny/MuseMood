def get_start_msg(name):
    return f"Приветствую👋, {name}!\nЧтобы узнать, что я умею - напиши\n/help"


def get_help_msg():
    return "Функционал бота:"


def get_menu_msg():
    return 'Меню'


def get_profile_msg():
    return 'Ваш профиль'


def get_playlists_msg():
    return 'ваши плейлисты'


def get_bot_start_msg():
    return "Бот успешно запущен"


def get_bot_stop_msg():
    return "Бот завершил работу"


def get_model_msg(model_res):
    return model_res


def get_model_error():
    return 'Что-то пошло не так :(\nПроверьте ссылку или формат аудио, затем попробуйте еще раз.'


def get_analysis_msg():
    return 'Пришлите ссылку или файл с вашим треком'


def get_garbage_msg():
    return 'Пропишите /start - чтобы начать!'


def get_audio_list_msg(playlist: str):
    return f'Треки {playlist}:'


def get_playlist_creation_msg():
    return 'Введите названия плейлиста'


def get_playlist_creation_title_msg(error_flag: bool):
    if error_flag:
        return 'Возникла непредвиденная ошибка, попробуйте позже :('
    return 'Плейлист создан'

