# Auth service

Auth Service предоставляет веб-API и Swagger по адресу http://0.0.0.0:8000/docs#/. В этом сервисе реализуются 
регистрация пользователя, вход (логин) и выдача JWT. Сервис хранит пользователей в базе (например SQLite или Postgres), 
хранит пароль только в виде хеша и формирует JWT с полями sub (id пользователя), role и временем жизни. Этот сервис 
является единственным местом, где выполняется “выпуск” токенов и управление пользователями.

**Минимально ожидаемые endpoint-ы:**

* POST `/auth/register` создаёт пользователя;
* POST `/auth/login` возвращает JWT;
* GET `/auth/me` возвращает профиль по JWT.

## Содержание

1. [Требования к проекту](docs/requirements.md);
2. [Конфигурация](docs/config.md);
3. [Запуск](docs/run.md);
4. [Регистрация пользователя](docs/register/README.md);
5. [Логирование](docs/login/README.md);
6. [Получение данных текущего пользователя](docs/me/README.md);
7. [Обновление access токена](docs/refresh_token/README.md);
8. [Health check](docs/health/README.md);
9. [Тестирование](docs/tests/README.md).