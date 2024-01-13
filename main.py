import json
import os
import easyocr
from PIL import Image
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import ContentType

download_path = 'PATH'
bot_token = 'TOKEN'
reader = easyocr.Reader(['ru'])
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

def load_keywords():
    with open('keywords.json', 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    return keywords

def save_keywords(keywords):
    with open('keywords.json', 'w', encoding='utf-8') as f:
        json.dump(keywords, f, ensure_ascii=False, indent=4)

def add_keyword(new_keyword):
    keywords = load_keywords()
    keywords.append(new_keyword)
    save_keywords(keywords)

def extract_new_keywords(text):
    return [word[1:] for word in text.split() if word.startswith('#')]

def recognize_text(image_path):
    image = Image.open(image_path)
    result = reader.readtext(image)
    text = ' '.join([item[1] for item in result])
    return text

@dp.message_handler(commands=['addkeyword'])
async def add_keyword_command(message: types.Message):
    user_id = message.from_user.id
    if user_id == 747530338 or user_id == 587763577:
        if len(message.text.split()) > 1:
            new_keyword = message.text.split()[1]
            add_keyword(new_keyword)
            await message.reply(f'Ключевое слово "{new_keyword}" добавлено в словарь.')
        else:
            await message.reply('Пожалуйста, укажите ключевое слово после команды.')

@dp.message_handler(content_types=ContentType.PHOTO)
async def handle_image(message: types.Message):
    file_id = message.photo[-1].file_id
    file_path = download_path + file_id + '.jpg'
    await bot.download_file_by_id(file_id, file_path)
    text = recognize_text(file_path)
    keywords = load_keywords()
    if any(keyword in text for keyword in keywords):
        await message.delete()
        response = f'Изображение содержит ключевые слова и было удалено.'
        os.remove(file_path)
    else:
        response = 'Изображение не содержит ключевых слов'
    await message.reply(response)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
