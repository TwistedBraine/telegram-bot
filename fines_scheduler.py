# -*- coding: utf-8 -*-
import schedule
import time
import threading
from datetime import datetime
from data.fines_database import fines_db

def send_daily_fine(bot, chat_id=None):
    """Отправить ежедневный штраф"""
    try:
        print(f"🕐 Попытка отправки ежедневного штрафа в {datetime.now()}")
        
        # ВАЖНО: Если chat_id не указан, используем сохраненный или дефолтный
        if not chat_id:
            # Сначала пробуем найти СЕГОДНЯШНИЙ штраф
            today_fine = fines_db.get_today_fine()
            if today_fine:
                chat_id = today_fine[6]  # 6-й элемент - chat_id
                print(f"📞 Используем chat_id из сегодняшнего штрафа: {chat_id}")
            else:
                # Если сегодняшнего нет, берем ВЧЕРАШНИЙ
                yesterday_data = fines_db.get_yesterday_message_id()
                if yesterday_data:
                    chat_id = yesterday_data[1]  # chat_id
                    print(f"📞 Используем chat_id из вчерашнего штрафа: {chat_id}")
                else:
                    # Если вообще нет истории - используем дефолтный chat_id
                    chat_id = -752589679  # Группа "604 МАРШРУТ"
                    print(f"📞 Используем дефолтный chat_id: {chat_id}")
        
        # Удаляем вчерашнее сообщение (только если тот же чат)
        yesterday_data = fines_db.get_yesterday_message_id()
        if yesterday_data:
            try:
                yesterday_message_id, yesterday_chat_id = yesterday_data
                if yesterday_chat_id == chat_id:  # Удаляем только если тот же чат
                    bot.delete_message(yesterday_chat_id, yesterday_message_id)
                    print(f"✅ Удален вчерашний штраф: {yesterday_message_id}")
            except Exception as e:
                print(f"⚠️ Не удалось удалить вчерашний штраф: {e}")
        
        # Получаем случайный штраф
        fine_data = fines_db.get_random_fine()
        if not fine_data:
            print("❌ Не удалось получить случайный штраф")
            return
        
        # Формируем сообщение
        today = datetime.now().strftime("%d.%m.%Y")
        message_text = f"""🚨 <b>ШТРАФ ДНЯ</b> | {today}

📁 <b>Раздел:</b> {fine_data['category']}
📝 <b>Статья:</b> {fine_data['article']}
⚖️ <b>Нарушение:</b> {fine_data['description']}
💰 <b>Штраф:</b> {fine_data['fine']}

💡 <i>{fine_data['advice']}</i>"""
        
        # Отправляем сообщение С ОТКЛЮЧЕННЫМ ПРЕДПРОСМОТРОМ
        sent_message = bot.send_message(
            chat_id,
            message_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
        # Сохраняем в базу
        fines_db.save_today_fine(
            fine_data['category'],
            fine_data['article'],
            fine_data['description'],
            fine_data['fine'],
            sent_message.message_id,
            chat_id
        )
        
        print(f"✅ Отправлен ежедневный штраф: {fine_data['article']} в чат {chat_id}")
        
    except Exception as e:
        print(f"❌ Ошибка отправки ежедневного штрафа: {e}")

def schedule_daily_fine(bot):
    """Настроить ежедневную отправку"""
    # Очищаем предыдущие задания
    schedule.clear()
    
    # Ставим новое задание
    schedule.every().day.at("10:00").do(send_daily_fine, bot=bot)
    print("✅ Настроена ежедневная отправка штрафов в 10:00")
    
    # Запускаем планировщик в отдельном потоке
    def run_scheduler():
        print("🔄 Планировщик штрафов запущен...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # Проверяем каждые 30 секунд
            except Exception as e:
                print(f"❌ Ошибка в планировщике: {e}")
                time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

def send_manual_fine(bot, chat_id):
    """Ручная отправка штрафа (для теста)"""
    print("🔧 Ручная отправка штрафа...")
    send_daily_fine(bot, chat_id)