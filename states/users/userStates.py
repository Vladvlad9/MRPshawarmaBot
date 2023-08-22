from aiogram.dispatcher.filters.state import StatesGroup, State


class UserStates(StatesGroup):
    USERNAME = State()
    Phone = State()
    Time = State()
    DESCRIPTION = State()
    BankCard = State()

    Confirmation = State()
    SendingAdmins = State()

    Quantity = State()
    WriteUser = State()

    Question = State()

