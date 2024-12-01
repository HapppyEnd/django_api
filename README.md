
## Описание проекта

Данный проект представляет собой API для управления пользователями и их рефералами. Он реализован с использованием Django REST Framework и предоставляет функционал для регистрации, авторизации, а также работы с реферальными кодами.

## Установка

### Требования

- Python 3.x
- Django
- Django REST Framework
- Django REST Framework Simple JWT
- drf-spectacular
- Docker, Docker compose

### Установка зависимостей

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/HapppyEnd/django_api.git
   ```

2. Настройка .env файла
    Создайте файл .env в корневом каталоге проекта и добавьте в него необходимые параметры конфигурации. Пример содержимого файла:

   ```bash
    PPOSTGRES_DB=<имя БД>
    POSTGRES_USER=<имя пользователя>
    POSTGRES_PASSWORD=<пароль>
    DB_NAME=<имя БД>
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=<секретный ключ Django>
    DEBUG=<режим DEBUG True/False>
    ALLOWED_HOSTS=<разрешенные хосты>
    CORS_ALLOWED_ORIGINS=<разрешенные хосты>
   ```

3. Запуск: 
    ```bash
    cd deploy
    docker compose -f docker-compose-prod.yml up -d
    ```

4. Настройки backenda:
    ```bash
    docker compose -f docker-compose.yml exec backend python manage.py migrate
    docker compose -f docker-compose.yml exec backend python manage.py collectstatic
    docker compose -f docker-compose.yml exec backend cp -r /app/static/. /app/backend_static/static/
    docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
    ```

## Использование API

### Эндпоинты

#### Регистрация и авторизация пользователя

- **URL**: `/auth/`
- **Метод**: `POST`
- **Тело запроса**:
    ```json
    {
        "phone_number": "Ваш номер телефона",
        "verified_code": "4-значный проверочный код (необязательно)"
    }
    ```
- **Ответ**:
    - **200 OK**: Возвращает проверочный код, если указан только номер, и токены доступа, если указан телефон и проверочный код.
    - **400 Bad Request**: Ошибки валидации.

#### Получение профиля пользователя или добавление реферального кода

- **URL**: `/users/me/`
- **Методы**: `GET`, `PATCH`
- **GET**: Возвращает информацию о пользователе.
- **PATCH**: Позволяет добавить реферальный код.
- **Тело запроса** (для PATCH):
    ```json
    {
        "reference_code": "Ваш реферальный код"
    }
    ```
- **Ответ**:
    - **200 OK**: Профиль пользователя или реферальный код успешно добавлен.
    - **400 Bad Request**: Ошибки валидации.
    - **404 Not Found**: Реферальный код не найден.

#### Получение списка всех пользователей

- **URL**: `/users/`
- **Метод**: `GET`
- **Ответ**:
    - **200 OK**: Список пользователей успешно получен.

#### Получение пользователя по ID

- **URL**: `/users/{id}/`
- **Метод**: `GET`
- **Ответ**:
    - **200 OK**: Пользователь успешно найден.
    - **404 Not Found**: Пользователь с указанным ID не найден.

### Документация API

Документация API доступна по следующим адресам:

- [Swagger UI](http://localhost:8000/docs/)
- [ReDoc](http://localhost:8000/redoc/)


API доступен по следующему адресу: [https://www.happpyend.ru/api/](https://www.happpyend.ru/api/).
## Лицензия

Этот проект лицензирован под MIT License. См. файл [LICENSE](LICENSE) для получения подробной информации.