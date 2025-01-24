from flask_migrate import Migrate
from app import app
from models import db
migrate = Migrate(app, db)

# Функция для создания таблиц
def setup_database():
    with app.app_context():  # Создаем контекст приложения
        db.create_all()  # Создаем таблицы в базе данных
        print("Таблицы успешно созданы!")

# Запуск приложения
if __name__ == '__main__':
    setup_database()  # Создание таблиц
    app.run(debug=True)