import logging
import configparser
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, executor, types, utils
import aiogram

BASE = Path(os.path.realpath(__file__))
os.chdir(BASE.parent)

config = configparser.ConfigParser()
config.read("secret_data/config.ini")
logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%y-%m-%d %H:%M')
bot = Bot(token=config['credentials']['telegram-api'])
dp = Dispatcher(bot)

# Из res создаём словарь строк для UI
def res_(filename: str):
    return open(filename, 'r').read()
res_dict = {}
for file in Path("res").iterdir():
    res_dict[file.stem] = res_(file)


@dp.message_handler(commands = "start")
async def send(message: types.Message): 
    await message.reply(res_dict["start"], parse_mode="html")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)