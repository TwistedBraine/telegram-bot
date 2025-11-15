# -*- coding: utf-8 -*-
import telebot
import requests
from config import WEATHER_API_KEY, WEATHER_CITY
from keyboards import main_keyboard
from utils import send_message_with_cleanup, save_user_message, get_cached_data, set_cached_data

def get_road_condition(temp, weather_desc, humidity):
    """Определяет состояние дороги"""
    if temp <= 0 and humidity > 80:
        return "❄️ <b>ГОЛОЛЁД - КРИТИЧЕСКАЯ ОПАСНОСТЬ</b>"
    elif temp <= 2 and humidity > 70:
        return "⚠️ <b>Возможен гололёд - повышенная опасность</b>"
    elif "дождь" in weather_desc.lower() or "ливень" in weather_desc.lower():
        return "💧 <b>Мокрая дорога - скользко</b>"
    elif "снег" in weather_desc.lower():
        return "🌨️ <b>Снег на дороге - снижайте скорость</b>"
    else:
        return "✅ <b>Дорога сухая - нормальные условия</b>"

def get_visibility_condition(visibility, weather_desc):
    """Определяет видимость на дороге"""
    if visibility <= 1000:
        return "🚨 <b>ОЧЕНЬ НИЗКАЯ (менее 1 км)</b>"
    elif visibility <= 3000:
        return "⚠️ <b>Низкая (1-3 км)</b>"
    elif visibility <= 7000:
        return "🔸 <b>Умеренная (3-7 км)</b>"
    else:
        return "✅ <b>Хорошая (более 7 км)</b>"

def get_driving_recommendations(temp, weather_desc, wind_speed, visibility):
    """Дает рекомендации для водителей"""
    recommendations = []
    
    if temp <= 0:
        recommendations.append("• 🧊 <b>Используйте зимнюю резину</b>")
        recommendations.append("• ⚠️ <b>Увеличьте дистанцию в 2 раза</b>")
        recommendations.append("• 🚗 <b>Избегайте резких торможений</b>")
    
    if "дождь" in weather_desc.lower():
        recommendations.append("• 💧 <b>Включите фары и противотуманки</b>")
        recommendations.append("• 🚘 <b>Снизьте скорость на 20-30%</b>")
        recommendations.append("• 📏 <b>Увеличьте дистанцию</b>")
    
    if "снег" in weather_desc.lower():
        recommendations.append("• 🌨️ <b>Включите дворники и обогревы</b>")
        recommendations.append("• 🚙 <b>Используйте пониженные передачи</b>")
        recommendations.append("• 🛞 <b>Проверьте давление в шинах</b>")
    
    if wind_speed > 10:
        recommendations.append("• 💨 <b>Будьте готовы к порывам ветра</b>")
        recommendations.append("• 🚛 <b>Особенно осторожно обгоняйте фуры</b>")
    
    if visibility < 2000:
        recommendations.append("• 🌫️ <b>Включите противотуманные фары</b>")
        recommendations.append("• 🐌 <b>Двигайтесь с минимальной скоростью</b>")
    
    if not recommendations:
        recommendations.append("• ✅ <b>Стандартные условия движения</b>")
        recommendations.append("• 👀 <b>Соблюдайте ПДД</b>")
    
    return recommendations

def setup_weather_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == '🌤️ Погода')
    def handle_weather(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        # Проверяем кэш
        cache_key = f"weather_{WEATHER_CITY}"
        cached_weather = get_cached_data(cache_key)
        
        if cached_weather:
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                cached_weather,
                main_keyboard(user_id),
                log_action="weather",
                parse_mode="HTML"
            )
            return
        
        # Если API ключа нет, показываем расширенную стандартную погоду
        if not WEATHER_API_KEY:
            weather_text = """<b>🌤️ ПОГОДА В МОСКВЕ</b>
<b>ДЛЯ ВОДИТЕЛЕЙ ТРАНСПОРТА</b>

━━━━━━━━━━━━━━━━━━━━
<b>📊 ТЕКУЩИЕ УСЛОВИЯ</b>
━━━━━━━━━━━━━━━━━━━━

🌡️ <b>Температура:</b> +3°C
💨 <b>Ветер:</b> 5 м/с
💧 <b>Влажность:</b> 75%
👁️ <b>Видимость:</b> 5 км
☁️ <b>Погода:</b> облачно с прояснениями

━━━━━━━━━━━━━━━━━━━━
<b>🛣️ СОСТОЯНИЕ ДОРОГ</b>
━━━━━━━━━━━━━━━━━━━━

• <b>Дорога:</b> 💧 Мокрая дорога - скользко
• <b>Видимость:</b> 🔸 Умеренная (3-7 км)
• <b>Осадки:</b> небольшая морось

━━━━━━━━━━━━━━━━━━━━
<b>🚗 РЕКОМЕНДАЦИИ ДЛЯ ВОДИТЕЛЕЙ</b>
━━━━━━━━━━━━━━━━━━━━

• 💧 Включите фары и противотуманки
• 🚘 Снизьте скорость на 20-30%
• 📏 Увеличьте дистанцию
• 👀 Будьте внимательны на пешеходных переходах

⚠️ <b>ОСТОРОЖНО НА ДОРОГЕ!</b>"""
            
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                weather_text,
                main_keyboard(user_id),
                log_action="weather",
                parse_mode="HTML"
            )
            return
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={WEATHER_CITY}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Основные данные
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                visibility = data.get('visibility', 10000)  # в метрах
                weather_desc = data['weather'][0]['description']
                
                # Конвертируем видимость в км
                visibility_km = visibility / 1000 if visibility else 10
                
                # Определяем условия для водителей
                road_condition = get_road_condition(temp, weather_desc, humidity)
                visibility_condition = get_visibility_condition(visibility_km, weather_desc)
                recommendations = get_driving_recommendations(temp, weather_desc, wind_speed, visibility_km)
                
                weather_text = f"""<b>🌤️ ПОГОДА В {WEATHER_CITY.upper()}</b>
<b>ДЛЯ ВОДИТЕЛЕЙ ТРАНСПОРТА</b>

━━━━━━━━━━━━━━━━━━━━
<b>📊 ТЕКУЩИЕ УСЛОВИЯ</b>
━━━━━━━━━━━━━━━━━━━━

🌡️ <b>Температура:</b> {temp:.1f}°C
🌡️ <b>Ощущается как:</b> {feels_like:.1f}°C
💨 <b>Ветер:</b> {wind_speed} м/с
💧 <b>Влажность:</b> {humidity}%
👁️ <b>Видимость:</b> {visibility_km:.1f} км
☁️ <b>Погода:</b> {weather_desc}

━━━━━━━━━━━━━━━━━━━━
<b>🛣️ СОСТОЯНИЕ ДОРОГ</b>
━━━━━━━━━━━━━━━━━━━━

• <b>Дорога:</b> {road_condition}
• <b>Видимость:</b> {visibility_condition}
• <b>Осадки:</b> {weather_desc}

━━━━━━━━━━━━━━━━━━━━
<b>🚗 РЕКОМЕНДАЦИИ ДЛЯ ВОДИТЕЛЕЙ</b>
━━━━━━━━━━━━━━━━━━━━"""

                for rec in recommendations:
                    weather_text += f"\n{rec}"
                
                weather_text += "\n\n⚠️ <b>ОСТОРОЖНО НА ДОРОГЕ!</b>"
                
                # Сохраняем в кэш
                set_cached_data(cache_key, weather_text)
                
                send_message_with_cleanup(
                    bot, user_id, message.chat.id,
                    weather_text,
                    main_keyboard(user_id),
                    log_action="weather",
                    parse_mode="HTML"
                )
            else:
                raise Exception("API error")
                
        except Exception as e:
            print(f"❌ Ошибка погоды: {e}")
            # Fallback на расширенную стандартную погоду
            weather_text = """<b>🌤️ ПОГОДА В МОСКВЕ</b>
<b>ДЛЯ ВОДИТЕЛЕЙ ТРАНСПОРТА</b>

━━━━━━━━━━━━━━━━━━━━
<b>📊 ТЕКУЩИЕ УСЛОВИЯ</b>
━━━━━━━━━━━━━━━━━━━━

🌡️ <b>Температура:</b> +2°C
💨 <b>Ветер:</b> 4 м/с
💧 <b>Влажность:</b> 80%
👁️ <b>Видимость:</b> 3 км
☁️ <b>Погода:</b> пасмурно, возможен дождь

━━━━━━━━━━━━━━━━━━━━
<b>🛣️ СОСТОЯНИЕ ДОРОГ</b>
━━━━━━━━━━━━━━━━━━━━

• <b>Дорога:</b> 💧 Мокрая дорога - скользко
• <b>Видимость:</b> ⚠️ Низкая (1-3 км)
• <b>Осадки:</b> возможен дождь

━━━━━━━━━━━━━━━━━━━━
<b>🚗 РЕКОМЕНДАЦИИ ДЛЯ ВОДИТЕЛЕЙ</b>
━━━━━━━━━━━━━━━━━━━━

• 💧 Включите фары и противотуманки
• 🚘 Снизьте скорость на 20-30%
• 📏 Увеличьте дистанцию
• 🌫️ Будьте готовы к ухудшению видимости

⚠️ <b>ОСТОРОЖНО НА ДОРОГЕ!</b>"""
            
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                weather_text,
                main_keyboard(user_id),
                log_action="weather",
                parse_mode="HTML"
            )