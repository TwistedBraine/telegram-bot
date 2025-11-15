# -*- coding: utf-8 -*-
import sys
import os
import telebot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from keyboards import main_keyboard
from utils import send_message_with_cleanup, save_user_message
from data.fines_database import fines_db
from fines_scheduler import send_manual_fine

def setup_daily_fines_handlers(bot):
    
    @bot.message_handler(func=lambda m: m.text == '🚨 Штраф дня')
    def handle_daily_fine(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        # Получаем сегодняшний штраф
        today_fine = fines_db.get_today_fine()
        
        if today_fine:
            # Показываем сегодняшний штраф
            date, category, article, description, fine, message_id, chat_id = today_fine
            today = date.split('-')[2] + '.' + date.split('-')[1] + '.' + date.split('-')[0]
            
            response = f"""🚨 <b>ШТРАФ ДНЯ</b> | {today}

📁 <b>Раздел:</b> {category}
📝 <b>Статья:</b> {article}
⚖️ <b>Нарушение:</b> {description}
💰 <b>Штраф:</b> {fine}

💡 <i>Ежедневно в 10:00 новый штраф</i>"""
        else:
            # Если сегодняшнего штрафа нет, отправляем случайный
            fine_data = fines_db.get_random_fine()
            if fine_data:
                response = f"""🚨 <b>СЛУЧАЙНЫЙ ШТРАФ</b>

📁 <b>Раздел:</b> {fine_data['category']}
📝 <b>Статья:</b> {fine_data['article']}
⚖️ <b>Нарушение:</b> {fine_data['description']}
💰 <b>Штраф:</b> {fine_data['fine']}

💡 <i>{fine_data['advice']}</i>"""
            else:
                response = "❌ <b>Не удалось загрузить информацию о штрафах</b>"
        
        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            response,
            main_keyboard(user_id),
            parse_mode="HTML"
        )
    
    # Команда для админа - принудительная отправка штрафа
    @bot.message_handler(commands=['sendfine'])
    def handle_send_fine(message):
        user_id = message.from_user.id
        if user_id != 130123754:  # Только для админа
            return
        
        send_manual_fine(bot, message.chat.id)
        bot.send_message(message.chat.id, "✅ Штраф отправлен вручную")

    # Команда для просмотра всех разделов штрафов
    @bot.message_handler(commands=['fines'])
    def handle_fines_list(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        from data.fines_database import FINES_DATA
        
        response = "📋 <b>РАЗДЕЛЫ ШТРАФОВ</b>\n\n"
        
        for category, fines in FINES_DATA.items():
            response += f"<b>{category}</b>\n"
            for fine in fines[:2]:  # Показываем по 2 штрафа из каждого раздела
                response += f"• {fine['article']}: {fine['description'][:50]}...\n"
            response += "\n"
        
        response += "💡 <i>Используйте «🚨 Штраф дня» для просмотра текущего штрафа</i>"
        
        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            response,
            main_keyboard(user_id),
            parse_mode="HTML"
        )