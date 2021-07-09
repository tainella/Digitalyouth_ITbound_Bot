"""
Обработчики не зависящие от типов юзеров
"""
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from loguru import logger

from .utils import res_dict


# TODO нормальное info
async def info_handler(message: types.Message):
    await message.answer(res_dict["info"], parse_mode="html")


# TODO нормальное contacts
async def contacts_handler(message: types.Message):
    await message.answer(res_dict["contacts"], parse_mode="html")


async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Все:
    Отмена действий через команду или сообщение
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('<i>Отменено.</i>', parse_mode="html")


async def cancel_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback_query.answer('Вы и так ничего не делаете:)')
    else:
        await state.finish()
        await callback_query.message.delete()
        await callback_query.message.answer('Отменено')
        await callback_query.answer()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(info_handler, commands='info')
    dp.register_message_handler(contacts_handler, commands='contacts')

    dp.register_message_handler(cancel_handler, state='*', commands='cancel')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state='*')

    dp.register_callback_query_handler(cancel_callback_handler, lambda callback_query: callback_query.data == "cancel",
                                       state='*')

