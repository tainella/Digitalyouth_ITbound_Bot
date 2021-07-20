from typing import Union

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from ...db.models import Task, User
from ...db.base import session_scope
from ...db.utils import get_all_interests
from ..utils.general_utils import res_dict, get_or_create_user, add_task
from ..utils.representative_utils import generate_reply_keyboard_for_tasks_done, \
    generate_reply_keyboard_for_tasks_spheres, generate_reply_keyboard_for_tasks_start, \
    generate_reply_keyboard_for_tasks
from ..fsm_states import CreateTask


async def create_task_start_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Подтверждение правильности введённых данных задачи
    """
    async with state.proxy() as data:
        to_return = f"Подтвердите правильность составленной задачи\n<i>Название:</i>\n{data['name']}\n\n"
        to_return += f"<i>Описание:</i>\n{data['description']}\n\n"
        to_return += f"<i>Сферы разработки:</i>\n{', '.join(filter(lambda x: data['spheres'][x], data['spheres']))}"
    await callback_query.message.edit_text(to_return, parse_mode="html")
    await callback_query.message.edit_reply_markup(reply_markup=generate_reply_keyboard_for_tasks_done())
    await CreateTask.next()
    await callback_query.answer()


async def create_task_done_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Отправка данных задачи на модерацию
    """
    async with state.proxy() as data:
        # Берём словарь "название_сферы: используется ли она" и генерим словарь истинных сфер
        data['spheres'] = list(filter(lambda x: data['spheres'][x], data['spheres']))

    await callback_query.message.answer(f'Задание <i>"{data["name"]}"</i> было отправлено на проверку модератору.',
                                        parse_mode="html")
    with session_scope() as session:
        await add_task(session, callback_query, data['name'], data['description'], data['spheres'])

    await callback_query.answer()
    await state.finish()


async def create_task_sphere_choice_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Выбор сфер разработки задачи
    """
    async with state.proxy() as data:
        data['spheres'][callback_query.data] = not data['spheres'][callback_query.data]

    await callback_query.message.edit_reply_markup(await generate_reply_keyboard_for_tasks_spheres(state))
    await callback_query.answer()


async def create_task_name_choice_handler(callback_query: types.CallbackQuery):
    """
    Выбор названия задачи
    """
    await callback_query.answer()
    await callback_query.message.delete()
    await CreateTask.name.set()
    await callback_query.message.answer("Введите <b>название задачи</b>\n(не более 50 символов)", parse_mode="html",
                                        reply_markup=generate_reply_keyboard_for_tasks_start())


async def create_task_description_choice_handler(update: Union[types.CallbackQuery, types.Message], state: FSMContext):
    """
    Выбор описания задачи и обработка неправильного названия
    """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await CreateTask.description.set()
        await message.answer("Введите <b>описание задачи</b>\n(не более 2000 символов)", parse_mode="html",
                             reply_markup=generate_reply_keyboard_for_tasks())
    else:
        message = update
        if len(message.text) > 50:
            await message.answer(
                f"Ошибка, название должно быть не более 50 символов.\n(Введено {len(message.text)} символов)\n\n"
                f"Введите <b>другое название задачи</b>\n(не более 50 символов)",
                parse_mode="html", reply_markup=generate_reply_keyboard_for_tasks_start())
        elif message.text in ["Помощь", "Добавить задачу", "История задач", "Текущие задачи"]:
            await message.answer(
                'Ошибка, неправильное название.\n\nВведите <b>другое название задачи</b>\n(не более 50 символов)\nДля '
                'отмены создания задания, нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=generate_reply_keyboard_for_tasks_start())
        else:
            async with state.proxy() as data:
                data['name'] = message.text

            await CreateTask.next()
            await message.answer("Введите <b>описание задачи</b>\n(не более 2000 символов)", parse_mode="html",
                                 reply_markup=generate_reply_keyboard_for_tasks())


async def create_task_sphere_handler(update: Union[types.CallbackQuery, types.Message], state: FSMContext):
    """
    Выбор сферы разработки и обработка неправильного описания
    """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await CreateTask.spheres.set()
        await message.answer("Выберите сферы разработки",
                             reply_markup=await generate_reply_keyboard_for_tasks_spheres(state))
    else:
        message = update
        if len(message.text) > 2000:
            await message.answer(
                "Ошибка, описание должно быть не более 2000 символов.\n(Введено {len(message.text)} "
                "символов)\n\nВведите <b>другое описание задачи</b>\n(не более 3000 символов)",
                parse_mode="html", reply_markup=generate_reply_keyboard_for_tasks())
        elif message.text in ["Помощь", "Добавить задачу", "История задач", "Текущие задачи"]:
            await message.answer(
                'Ошибка, неправильное описание.\n\nВведите <b>другое описание задачи</b>\n(не более 2000 '
                'символов)\nДля отмены создания задания, нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=generate_reply_keyboard_for_tasks())
        else:
            async with state.proxy() as data:
                data['description'] = message.text
                with session_scope() as session:
                    data['spheres'] = {interest: False for interest in get_all_interests(session)}

            await CreateTask.next()
            await message.answer("Выберите сферы разработки",
                                 reply_markup=await generate_reply_keyboard_for_tasks_spheres(
                                     state))


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(create_task_start_handler, lambda callback_query: callback_query.data == "done",
                                       state=CreateTask.spheres)
    dp.register_callback_query_handler(create_task_done_handler, lambda callback_query: callback_query.data == "done",
                                       state=CreateTask.done)
    dp.register_callback_query_handler(create_task_sphere_choice_handler,
                                       lambda callback_query: callback_query.data != "back", state=CreateTask.spheres)
    dp.register_callback_query_handler(create_task_name_choice_handler,
                                       lambda callback_query: callback_query.data == "back",
                                       state=CreateTask.description)

    dp.register_callback_query_handler(create_task_description_choice_handler,
                                       lambda callback_query: callback_query.data == "back", state=CreateTask.spheres)
    dp.message_handler(create_task_description_choice_handler, state=CreateTask.name)

    dp.register_callback_query_handler(create_task_sphere_handler,
                                       lambda callback_query: callback_query.data == "back", state=CreateTask.done)
    dp.message_handler(create_task_sphere_handler, state=CreateTask.description)
