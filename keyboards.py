# -*- coding: utf-8 -*-
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard(user_id=None):
    print(f"🔧 [KEYBOARD] Создание клавиатуры для user_id: {user_id}")
    print(f"🔧 [KEYBOARD] user_id == 130123754: {user_id == 130123754}")
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        '🔍 Поиск водителей',
        '📞 Телефоны', 
        '🚌 Маршруты',
        '🏥 Профосмотр',
        '🏢 Филиалы',
        '🌤️ Погода',
        '🔧 Текущий механик',
        '⛽ Расчет топлива',
        '🚨 Штраф дня'  # Новая кнопка
    ]
    
    if user_id == 130123754:
        buttons.append('📊 Статистика')
        print(f"✅ [KEYBOARD] Кнопка 'Статистика' ДОБАВЛЕНА")
    
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(KeyboardButton(buttons[i]), KeyboardButton(buttons[i+1]))
        else:
            keyboard.add(KeyboardButton(buttons[i]))
    
    return keyboard

def phones_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(KeyboardButton('📞 Телефоны парка'))
    keyboard.add(KeyboardButton('👔 Телефоны руководства'))
    keyboard.add(KeyboardButton('🛰️ Телефоны ГЛОНАСС'))
    keyboard.add(KeyboardButton('⬅️ Главное меню'))
    return keyboard

def register_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton('📱 Поделиться номером', request_contact=True))
    return keyboard