from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from sqlalchemy.orm.session import Session

from ...db.utils import get_opened_tasks, get_tasks_for_user, get_specialist_spheres
from ...db.models import User
from ..utils.general_utils import res_dict, generate_inline_keyboard_for_tasks


async def send_profile(db_user: User, message: types.Message):
    to_send = res_dict['profile_specialist'].format(db_user.real_fullname, db_user.phone_n,
                                                    ', '.join(get_specialist_spheres(db_user)),
                                                    "Подписан" if db_user.specialist.is_subscribed else "Не подписан",
                                                    len(get_tasks_for_user(db_user, ('awaiting_confirmation',
                                                                                     'awaiting_specialist',
                                                                                     'in_work'))),
                                                    len(get_tasks_for_user(db_user, ('closed_with_success',
                                                                                     'canceled_by_represented',
                                                                                     'closed_by_other_reason'))))

    keyboard = InlineKeyboardMarkup()
    keyboard.insert(InlineKeyboardButton('Редактировать', callback_data='edit_profile'))
    await message.answer(to_send, parse_mode='html', reply_markup=keyboard)


# async def generate_inline_keyboard_for_tasks(state: FSMContext, page_n: int, type_: str):
#     async with state.proxy() as state_data:
#         tasks_list: List[Task] = state_data[f'tasks_{type_}']
#     if page_n * 9 > len(tasks_list):
#         return False
#     else:
#         reply_markup = types.InlineKeyboardMarkup()
#         for index, task in enumerate(tasks_list[page_n * 9:(page_n + 1) * 9]):
#             callback_data_to_input = f"task_info {task.id_} {page_n} {type_}"
#             reply_markup.add(types.InlineKeyboardButton(f"{page_n * 9 + (index + 1)}. {task.name}"[:60],
#                                                         callback_data=callback_data_to_input))
#         reply_markup.row()
#         # cp_tasks - change page in tasks
#         if page_n != 0:
#             reply_markup.insert(types.InlineKeyboardButton("<<", callback_data=f'cp_tasks {page_n - 1} {type_}'))
#         if (page_n + 1) * 9 < len(tasks_list):
#             reply_markup.insert(types.InlineKeyboardButton(">>", callback_data=f'cp_tasks {page_n + 1} {type_}'))
#         return reply_markup


async def tasks_history(db_user, message: types.Message, state: FSMContext):
    tasks = get_tasks_for_user(db_user, ('closed_with_success', 'canceled_by_represented', 'closed_by_other_reason'))
    if tasks:
        async with state.proxy() as state_data:
            state_data['tasks_history'] = tasks
        await message.answer('История задач, которые Вы выполнили. \nЧтобы получить больше информации, нажмите на '
                             'задачу.',
                             parse_mode='html',
                             reply_markup=await generate_inline_keyboard_for_tasks(state, 0, 'history'))
    else:
        await message.answer('На данный момент вы не выполнили ни одной задачи',)


async def tasks_current(db_user, message: types.Message, state: FSMContext):
    tasks = get_tasks_for_user(db_user, ('awaiting_confirmation', 'awaiting_specialist', 'in_work'))
    if tasks:
        async with state.proxy() as state_data:
            state_data['tasks_current'] = tasks
        await message.answer('Текущие задачи, которые Вы сейчас выполняете. \nЧтобы получить больше информации и '
                             'редактировать, нажмите на задачу.', parse_mode='html',
                             reply_markup=await generate_inline_keyboard_for_tasks(state, 0, 'current'))
    else:
        await message.answer('На данный момент вы не выполняете какие-либо задачи, чтобы получить задание, зайдите в '
                             'меню "Список доступных задач"')


async def available_tasks(session: Session, db_user: User, message: types.Message, state: FSMContext):
    tasks = get_opened_tasks(session, tuple(association.sphere for association in db_user.specialist.spheres))
    if tasks:
        async with state.proxy() as state_data:
            state_data['tasks_available'] = tasks
        await message.answer('Доступные на взятие задачи. \nЧтобы получить больше информации, нажмите на задачу.',
                             parse_mode='html',
                             reply_markup=await generate_inline_keyboard_for_tasks(state, 0, 'available'))
    else:
        await message.answer('Нет доступных на взятие задач, вы можете поменять предпочтения в меню "Настройки"')

