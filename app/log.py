import functools
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

# 1. Создаём папку для логов, если её нет
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 2. Настраиваем ротационный хэндлер, пишущий каждый день новый файл
log_file = os.path.join(LOG_DIR, "app.log")
handler = TimedRotatingFileHandler(
    filename=log_file,
    when="midnight",     # ротация в полночь
    interval=1,          # каждые 1 сутки
    backupCount=30,      # храним 30 последних файлов
    encoding="utf-8",
)
handler.suffix = "%Y-%m-%d.log"  # суффикс у файла: app.log.2025-09-22.log.2025-09-01.log.YYYY-MM-DD
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)

# 3. Конфигурируем корневой логгер
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()
logger.addHandler(handler)


def log_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        logger.info(f"Функция '{func.__name__}' вызвана")
        logger.info(f"Время выполнения: {elapsed:.4f} секунд")
        return result
    return wrapper
