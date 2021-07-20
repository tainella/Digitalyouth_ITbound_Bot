from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateTask(StatesGroup):
    """
    КА создания задачи для создания таска представителем
    """
    name = State()
    description = State()
    spheres = State()
    done = State()


class Registration(StatesGroup):
    """
    КА создания задачи для регистрации в системе
    """
    fullname = State()
    phone = State()
    wished_role = State()
    done = State()
