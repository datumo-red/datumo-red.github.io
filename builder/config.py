import os

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_PATH = os.path.join(BASE_PATH, 'docs')
API_KEY = os.getenv('INPUT_API_KEY', '') or os.getenv('API_KEY', '')

DATA_URL = 'https://docs.google.com/spreadsheets/d/1OkOBkaHpTmvNrFXy7ukeFgnh_4PKdaL7zke3OxyQs_4'