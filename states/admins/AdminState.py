from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminState(StatesGroup):
    NewsletterText = State()
    NewsletterPhoto = State()