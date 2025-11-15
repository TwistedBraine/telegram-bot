# -*- coding: utf-8 -*-
import time
from database import user_db

# Кэш для данных
cache_data = {}
CACHE_TIMEOUTS = {
    'weather': 1800,  # 30 минут
    'search': 300,    # 5 минут
    'stats': 600      # 10 минут
}

def get_cached_data(key):
    """Получить данные из кэша"""
    if key in cache_data:
        data, timestamp = cache_data[key]
        cache_type = key.split('_')[0]
        if time.time() - timestamp < CACHE_TIMEOUTS.get(cache_type, 300):
            print(f"🔧 [CACHE] Использован кэш для: {key}")
            return data
        else:
            del cache_data[key]
            print(f"🔧 [CACHE] Удален устаревший кэш: {key}")
    return None

def set_cached_data(key, data):
    """Сохранить данные в кэш"""
    cache_data[key] = (data, time.time())
    print(f"🔧 [CACHE] Сохранен в кэш: {key}")

def send_message_with_cleanup(bot, user_id, chat_id, text, reply_markup=None, log_action=None, parse_mode=None):
    """Отправляет сообщение, предварительно удаляя предыдущие сообщения бота и пользователя"""
    
    print(f"🔧 [CLEANUP] Начало очистки для user_id: {user_id}, chat_id: {chat_id}")
    
    try:
        # Удаляем предыдущее сообщение бота
        last_message_id = user_db.get_last_bot_message(user_id)
        print(f"🔧 [CLEANUP] Последнее сообщение бота: {last_message_id}")
        
        if last_message_id:
            try:
                bot.delete_message(chat_id, last_message_id)
                print(f"✅ [CLEANUP] Удалено сообщение бота: {last_message_id}")
            except Exception as e:
                print(f"⚠️ [CLEANUP] Не удалось удалить сообщение бота {last_message_id}: {e}")
        
        # Удаляем ВСЕ сообщения пользователя
        deleted_count = user_db.delete_user_messages(bot, user_id, chat_id)
        print(f"✅ [CLEANUP] Удалено сообщений пользователя: {deleted_count}")
        
    except Exception as e:
        print(f"❌ [CLEANUP] Ошибка удаления сообщений: {e}")
    
    # Логируем действие если указано И пользователь не админ (чтобы не логировать тесты)
    if log_action and user_id != 130123754:
        try:
            user_db.log_usage(user_id, "User", log_action)
        except Exception as e:
            print(f"⚠️ Ошибка логирования: {e}")
    
    # Отправляем новое сообщение С ОТКЛЮЧЕННЫМ ПРЕДПРОСМОТРОМ
    sent_message = bot.send_message(
        chat_id,
        text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
        disable_web_page_preview=True
    )
    
    # Сохраняем ID нового сообщения бота
    try:
        user_db.save_last_bot_message(user_id, sent_message.message_id)
        print(f"💾 [CLEANUP] Сохранено новое сообщение бота: {sent_message.message_id}")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения сообщения бота: {e}")
    
    return sent_message

def save_user_message(user_id, message_id, chat_id):
    """Сохраняет сообщение пользователя для последующего удаления"""
    try:
        result = user_db.save_user_message(user_id, message_id, chat_id)
        print(f"💾 [SAVE] Сохранено сообщение пользователя {user_id}: {message_id} в чате {chat_id}")
        return result
    except Exception as e:
        print(f"❌ Ошибка сохранения сообщения пользователя: {e}")
        return False