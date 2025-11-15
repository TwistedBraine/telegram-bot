# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
WEATHER_CITY = 'Москва'
ADMIN_USER_ID = 130123754

if not BOT_TOKEN:
    print("❌ BOT_TOKEN не найден")