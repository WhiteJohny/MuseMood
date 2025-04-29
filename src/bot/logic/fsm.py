from aiogram.fsm.state import StatesGroup, State

from src.bot.logic.keyboards import get_main_menu_kb, get_analysis_kb, get_profile_kb
from src.bot.logic.views import get_menu_msg, get_analysis_msg, get_profile_msg, get_playlist_creation_msg


class User(StatesGroup):
    menu = State()
    analysis = State()
    profile = State()
    creation = State()


STATES = {
    User.menu: None,
    User.analysis: User.menu,
    User.profile: User.menu,
    User.creation: User.profile
}

KEYBOARDS = {
    User.menu: get_main_menu_kb,
    User.analysis: get_analysis_kb,
    User.profile: get_profile_kb,
    User.creation: get_analysis_kb
}

VIEWS = {
    User.menu: get_menu_msg,
    User.analysis: get_analysis_msg,
    User.profile: get_profile_msg,
    User.creation: get_playlist_creation_msg
}
