from typing import Union

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from ...db.models import Task, User, Specialist
from ...db.base import session_scope
from ...db.utils import get_all_interests
from ..utils.general_utils import res_dict, get_or_create_user, add_task, generate_inline_keyboard_back_cancel, \
    generate_inline_keyboard_cancel
from ..utils.registration_utils import generate_role_keyboard
from ..fsm_states import Registration


async def registration_fullname(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    await Registration.fullname.set()
    await callback_query.message.answer("Введите ФИО", parse_mode="html",
                                        reply_markup=generate_inline_keyboard_cancel())


async def registration_phone_n(update, state: FSMContext):
    """
    Ввели фамилию, ввод телефона
    """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await Registration.phone.set()
        await message.answer("Введите <b>свой телефонный номер</b>\n", parse_mode="html",
                             reply_markup=generate_inline_keyboard_back_cancel())
    else:
        message = update
        if len(message.text) > 50:
            await message.answer(
                f"Ошибка, ФИО должно быть не более 50 символов.\n(Введено {len(message.text)} символов)\n\nВведите <b>укороченную версию ФИО</b>\n(не более 50 символов)",
                parse_mode="html", reply_markup=generate_inline_keyboard_cancel())
        elif message.text in ["Помощь", "Регистрация"]:
            await message.answer(
                'Ошибка, неправильное ФИО.\n\nВведите <b>настоящее ФИО</b>\n(не более 50 символов)\nДля отмены регистрации нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=generate_inline_keyboard_cancel())
        else:
            async with state.proxy() as data:
                data['fullname'] = message.text

            await Registration.next()
            await message.answer("Введите <b>свой телефонный номер</b>\n", parse_mode="html",
                                 reply_markup=generate_inline_keyboard_back_cancel())


async def registration_role(update, state: FSMContext):
    """
    Ввели телефон, ввод желаемой роли
    """
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await Registration.wished_role.set()
        await message.answer("Кто вы?", reply_markup=await generate_role_keyboard())
    else:
        message = update
        # добавить проверку телефона
        if message.text in ["Помощь", "Регистрация"]:
            await message.answer(
                'Ошибка, неправильный телефонный номер.\n\nВведите <b>другой телефонный номер</b>\nДля отмены '
                'регистрации, нажмите <code>"Отмена"</code>',
                parse_mode="html", reply_markup=generate_inline_keyboard_back_cancel())
        else:
            async with state.proxy() as data:
                data['phone'] = message.text
            await Registration.next()
            await message.answer("Кто Вы?", reply_markup=generate_role_keyboard())


async def registration_done(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Регистрация:
    Отправка анкеты и данных
    """
    with session_scope() as session:
        user = await get_or_create_user(session, callback_query)
        if callback_query.data == 'wish_specialist':
            specialist = Specialist(user)
            session.add(specialist)
            await callback_query.message.answer("Регистрация прошла успешно, нажмите start для продолжения")

            # reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            # reply_keyboard.add(KeyboardButton('Список доступных задач'))
            # reply_keyboard.add(KeyboardButton('Текущие задачи'))
            # reply_keyboard.insert(KeyboardButton('История задач'))
            # reply_keyboard.add(KeyboardButton('Профиль'))
            # reply_keyboard.insert(KeyboardButton('Помощь'))
            # await callback_query.message.answer(res_dict["start"], parse_mode="html", reply_markup=reply_keyboard)
        else:
            if callback_query.data == 'wish_moderator':
                user.status = "wish_moderator"
            else:
                user.status = "wish_representative"
            await callback_query.message.answer("Ваша анкета была отправлена на рассмотрение модератором")
        async with state.proxy() as data:
            user.real_fullname = data['fullname']
            user.phone_n = data['phone']

        await callback_query.answer()
        await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(registration_phone_n,
                                       lambda callback_query: callback_query.data == "back", state=Registration.phone)

    dp.register_callback_query_handler(registration_phone_n, lambda callback_query: callback_query.data == "back",
                                       state=Registration.wished_role)
    dp.register_message_handler(registration_phone_n, state=Registration.fullname)

    dp.register_callback_query_handler(registration_role, lambda callback_query: callback_query.data == "back", state=Registration.done)
    dp.register_message_handler(registration_role, state=Registration.phone)

    dp.register_callback_query_handler(registration_done, state=Registration.wished_role)

