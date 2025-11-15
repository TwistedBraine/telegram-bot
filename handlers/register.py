# -*- coding: utf-8 -*-
import telebot
from database import user_db
from keyboards import main_keyboard
from utils import send_message_with_cleanup, save_user_message

def setup_register_handlers(bot):
    
    @bot.message_handler(content_types=['contact'])
    def handle_contact(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        if message.contact:
            phone = message.contact.phone_number
            username = message.from_user.first_name
            
            print(f"📱 Получен контакт: {phone} от пользователя {username}")
            
            normalized_phone = user_db.normalize_phone(phone)
            
            user_db.register_user(user_id, normalized_phone, username)
            
            is_employee = user_db.is_employee(normalized_phone)
            
            print(f"🔍 Проверка сотрудника: {normalized_phone} -> {is_employee}")
            
            if is_employee:
                response = f"""✅ Регистрация успешна!

📱 Ваш номер: {normalized_phone}
👥 Статус: сотрудник компании
🔍 Доступ к поиску: разрешен"""
            else:
                response = f"""✅ Регистрация успешна!

📱 Ваш номер: {normalized_phone}  
⚠️ Статус: пользователь
🔍 Доступ к поиску: ограничен

💡 Для доступа к поиску водителей обратитесь к администратору"""
            
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                response,
                main_keyboard(user_id),
                log_action="registration_success"
            )
            
            print(f"✅ Пользователь {user_id} зарегистрирован с номером {normalized_phone}, сотрудник: {is_employee}")
            
        else:
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "❌ Не удалось получить номер телефона.",
                main_keyboard(user_id)
            )