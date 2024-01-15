import json
import os
from dotenv import load_dotenv
from aiogram import Bot, types, Dispatcher
from aiogram.types import ContentType
import easyocr
from PIL import Image

load_dotenv()
download_path = './'
bot_token = 'token'
reader = easyocr.Reader(['ru'])
bot = Bot(token=bot_token)
dp = Dispatcher(bot)


async def load_keywords():
    with open('keywords.json', 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    return keywords


async def save_keywords(keywords):
    with open('keywords.json', 'w', encoding='utf-8') as f:
        json.dump(keywords, f, ensure_ascii=False, indent=4)


async def add_keyword(new_keyword):
    keywords = await load_keywords()
    keywords.append(new_keyword)
    await save_keywords(keywords)


async def remove_keyword(keyword_to_remove):
    keywords = await load_keywords()
    if keyword_to_remove in keywords:
        keywords.remove(keyword_to_remove)
        await save_keywords(keywords)


async def list_keywords():
    keywords = await load_keywords()
    return ', '.join(keywords)


def extract_new_keywords(text):
    return [word[1:] for word in text.split() if word.startswith('#')]


async def recognize_text(image_path):
    image = Image.open(image_path)
    result = reader.readtext(image)
    text = ' '.join([item[1] for item in result])
    return text


@dp.message_handler(commands=['addkeyword'])
async def add_keyword_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in {747530338, 587763577, 918288429}:
        if len(message.text.split()) > 1:
            new_keyword = message.text.split()[1]
            await add_keyword(new_keyword)
            await message.reply(f'Ключевое слово "{new_keyword}" добавлено в словарь.')
        else:
            await message.reply('Пожалуйста, укажите ключевое слово после команды.')


@dp.message_handler(commands=['removekeyword'])
async def remove_keyword_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in {747530338, 587763577, 918288429}:
        if len(message.text.split()) > 1:
            keyword_to_remove = message.text.split()[1]
            await remove_keyword(keyword_to_remove)
            await message.reply(f'Ключевое слово "{keyword_to_remove}" удалено из словаря.')
        else:
            await message.reply('Пожалуйста, укажите ключевое слово после команды.')


@dp.message_handler(commands=['listkeywords'])
async def list_keywords_command(message: types.Message):
    keywords_list = await list_keywords()
    await message.reply(f'Текущие ключевые слова: {keywords_list}')


@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_image(message: types.Message):
    file_id = message.photo[-1].file_id
    file_path = download_path + file_id + '.jpg'
    await bot.download_file_by_id(file_id, file_path)
    text = await recognize_text(file_path)
    keywords = await load_keywords()
    if any(keyword in text for keyword in keywords):
        await message.delete()
        response = f'Изображение содержит ключевые слова и было удалено.'
        os.remove(file_path)
    else:
        response = 'Изображение не содержит ключевых слов'
    print(response)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
