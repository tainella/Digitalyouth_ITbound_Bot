import logging
import configparser
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types, utils
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

import utils

BASE = Path(os.path.realpath(__file__))
os.chdir(BASE.parent)

config = configparser.ConfigParser()
config.read("secret_data/config.ini")
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%y-%m-%d %H:%M')
bot = Bot(token=config['credentials']['telegram-api'])
storage = MemoryStorage() # TODO перейти на redis storage
dp = Dispatcher(bot, storage=storage)


class CreateTask(StatesGroup):
    name = State()
    description = State()
    spheres = State()
    done = State()

# Из res создаём словарь строк для UI
def res_(filename: str):
    return open(filename, 'r').read()
res_dict = {}
for file in Path("res").iterdir():
    res_dict[file.stem] = res_(file)

def get_status(chat_id: int):
    # TODO получать статус из бд
    return "representative"

@dp.message_handler(commands = "start", state=None)
async def send(message: types.Message):
    """
    Сообщение приветствия + генерация reply клавы
    """
    # TODO добавить эмодзи
    user_status = get_status(message.chat.id) # moderator specialist representative
    reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if user_status == "moderator":
        reply_keyboard.add(KeyboardButton('Начать модерацию')) 
        reply_keyboard.insert(KeyboardButton('Помощь')) 
    elif user_status == "specialist":
        reply_keyboard.add(KeyboardButton('Список доступных задач')) 
        reply_keyboard.add(KeyboardButton('Текущие задачи')) 
        reply_keyboard.insert(KeyboardButton('История задач'))
        reply_keyboard.add(KeyboardButton('Настройки')) 
        reply_keyboard.insert(KeyboardButton('Помощь')) 
    elif user_status == "representative":
        reply_keyboard.add(KeyboardButton('Добавить задачу')) 
        reply_keyboard.add(KeyboardButton('Текущие задачи')) 
        reply_keyboard.insert(KeyboardButton('История задач')) 
        reply_keyboard.add(KeyboardButton('Помощь')) 
    else:
        reply_keyboard.add(KeyboardButton('Помощь')) 
    await message.answer(res_dict["start"], parse_mode="html", reply_markup=reply_keyboard)
    # print(message.from_user.get_mention(as_html=True))
    

@dp.message_handler(state='*', commands='/cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('<i>Отменено.</i>', parse_mode="html")

@dp.callback_query_handler(lambda callback_query: callback_query.data == "cancel" , state='*')
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    await state.finish()
    await callback_query.message.delete()
    await callback_query.message.answer('Отменено')


@dp.callback_query_handler(lambda callback_query: callback_query.data == "done", state=CreateTask.spheres)
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        to_return = f"Подтвердите правильность составленной задачи\n<i>Название:</i>\n{data['name']}\n\n"
        to_return += f"<i>Описание:</i>\n{data['description']}\n\n"
        to_return += f"<i>Сферы разработки:</i>\n{', '.join(filter(lambda x: data['spheres'][x], data['spheres']))}"
    await callback_query.message.edit_text(to_return, parse_mode="html")
    await callback_query.message.edit_reply_markup(reply_markup=utils.generate_reply_keyboard_for_tasks_done()) 
    await CreateTask.next()
    await callback_query.answer()


@dp.callback_query_handler(lambda callback_query: callback_query.data == "done", state=CreateTask.done)
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spheres'] = list(filter(lambda x: data['spheres'][x], data['spheres']))
        await callback_query.message.answer(f'Задание <i>"{data["name"]}"</i> было отправлено на проверку модерацией.', parse_mode="html")
        # TODO отсылать в БД
        await callback_query.answer()
    await state.finish()    


@dp.callback_query_handler(lambda callback_query: callback_query.data != "back", state=CreateTask.spheres)
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['spheres'][callback_query.data] = not data['spheres'][callback_query.data] 
    await callback_query.message.edit_reply_markup(await utils.generate_reply_keyboard_for_tasks_spheres(state)) 
    await callback_query.answer()


@dp.message_handler(state=None)
async def send(message: types.Message, state: FSMContext):
    user_status = get_status(message.chat.id) # moderator specialists representatives
    command = message.text
    if user_status == "moderator":
        if command == "Помощь":
            await message.answer(res_dict["help_moderator"], parse_mode="html")
        elif command == "Начать модерацию": 
            pass
    elif user_status == "specialist":
        if command == "Помощь":
            await message.answer(res_dict["help_specialist"], parse_mode="html")
        elif command == "Список доступных задач":
            pass
        elif command == "Текущие задачи":
            pass
        elif command == "История задач":
            pass
        elif command == "Настройки":
            pass
    elif user_status == "representative":
        if command == "Помощь":
            await message.answer(res_dict["help_representative"], parse_mode="html")
        elif command == "Добавить задачу":
            await message.answer("Введите название задачи(не более 50 символов)", reply_markup=utils.generate_reply_keyboard_for_tasks_start())
            await CreateTask.name.set()
        elif command == "История задач":
            pass
        elif command == "Текущие задачи":
            pass
    
@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=CreateTask.description)
async def send(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.delete()
    await CreateTask.name.set()
    await callback_query.message.answer("Введите название задачи(не более 50 символов)", reply_markup=utils.generate_reply_keyboard_for_tasks_start())
    


@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=CreateTask.spheres)
@dp.message_handler(state=CreateTask.name)
async def send(update, state: FSMContext):
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await CreateTask.description.set()
        await message.answer("Введите описание задачи(не более 3000 символов)", reply_markup=utils.generate_reply_keyboard_for_tasks())
    else:
        message = update
        if len(message.text) > 50:
            await message.answer("Ошибка, название должно быть не более 50 символов", reply_markup=utils.generate_reply_keyboard_for_tasks())
        else:
            async with state.proxy() as data:
                data['name'] = message.text

            await CreateTask.next()
            await message.answer("Введите описание задачи(не более 3000 символов)", reply_markup=utils.generate_reply_keyboard_for_tasks())
    

@dp.callback_query_handler(lambda callback_query: callback_query.data == "back", state=CreateTask.done)
@dp.message_handler(state=CreateTask.description)
async def send(update, state: FSMContext):
    if isinstance(update, types.CallbackQuery):
        message = update.message
        await update.answer()
        await update.message.delete()
        await CreateTask.spheres.set()
        await message.answer("Выберите сферы разработки", reply_markup=await utils.generate_reply_keyboard_for_tasks_spheres(state))
    else:
        message = update
        if len(message.text) > 2000:
            await message.answer("Ошибка, описание должно быть не более 2000 символов", reply_markup=utils.generate_reply_keyboard_for_tasks())
        else:
            async with state.proxy() as data:
                data['description'] = message.text
                data['spheres'] = {interest: False for interest in utils.get_all_interests()}

            await CreateTask.next()
            await message.answer("Выберите сферы разработки", reply_markup=await utils.generate_reply_keyboard_for_tasks_spheres(state))


@dp.callback_query_handler(state='*')
async def some_callback_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Ошибка, начните заного")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)