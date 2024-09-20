# Файл, содержащий переменные среды в виде обычных


# Подключение модулей Python
from os import getenv
from dotenv import load_dotenv


# Загрзука файла .env
load_dotenv()


# Переменная, содержащая токен бота в Телеграм
BOT_TOKEN: str = getenv("BOT_TOKEN")

# Переменная, содержащая Телеграм id владельца бота
PROXY_URL: str = getenv("PROXY_URL")

# Переменная, содержащая адрес прокси-сервера для PythonAnywhere
OWNER_TG_ID: int = int(getenv("OWNER_TG_ID"))

# Переменная, содержащая URL-адрес базы данных в SQLAlchemy
DB_URL: str = getenv("DB_URL")
