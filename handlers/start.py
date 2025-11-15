# -*- coding: utf-8 -*-
import telebot
from database import user_db
from keyboards import main_keyboard, register_keyboard
from utils import send_message_with_cleanup, save_user_message

def setup_start_handlers(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user_id = message.from_user.id
        print(f"🔔 Команда /start от пользователя {user_id}")
        
        # Сохраняем сообщение пользователя
        save_user_message(user_id, message.message_id, message.chat.id)
        
        if user_db.is_registered(user_id):
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "🚍 Добро пожаловать! Выберите раздел:",
                main_keyboard(user_id),
                log_action="start"
            )
        else:
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "Привет! 👋\nДля доступа нужна регистрация.\nНажмите кнопку ниже:",
                register_keyboard(),
                log_action="start_unregistered"
            )
    
    @bot.message_handler(func=lambda m: m.text == '⬅️ Главное меню')
    def handle_back(message):
        user_id = message.from_user.id
        print(f"🔔 Главное меню от пользователя {user_id}")
        
        # Сохраняем сообщение пользователя
        save_user_message(user_id, message.message_id, message.chat.id)
        
        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            "Главное меню:",
            main_keyboard(user_id),
            log_action="back_to_menu"
        )