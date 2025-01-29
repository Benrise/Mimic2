import os

# Параметры подключения к базе
DB_USER = os.getenv("DB_USER", "student")
DB_PASSWORD = os.getenv("DB_PASSWORD", "student_nmax")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "chat_db")

# Формируем строку подключения для psycopg2
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# API ChatGPT
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY", "")

# API Gigachat
GIGACHAT_API_KEY = os.getenv("GIGACHAT_API_KEY", "")

# Прокси для обхода блокировок
PROXY_URL = os.getenv("PROXY_URL", "")

INFERENCE_PORT = os.getenv("INFERENCE_PORT", "8001")

# Параметры модели
MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
CANDIDATE_LABELS = ["бот", "человек"]
