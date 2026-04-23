# Конфигурация приложения

**Шаблон файла:**

```
# === Приложение ===
APP_NAME=
ENV=

# === JWT настройки ===
JWT__ALG=
JWT__HEADER_NAME=

# Ключ для подписи JWT (заполняется один из следующих параметров):
JWT__SECRET__DATA=
JWT__SECRET__PATH=

# === Подключение к БД ===
DB__HOST=
DB__PORT=
DB__DB_NAME=
DB__USER=
DB__PASSWORD=
DB__DB_SCHEMA=
DB__DB_TYPE=

# Для тестирования на SQLite:
DB__TEST_DB_PATH=

# === Настройки Redis ===
REDIS__HOST=
REDIS__PORT=
REDIS__DB=
REDIS__PASSWORD=
REDIS__TIMEOUT=
REDIS__CACHE_TTL=
REDIS__IDEM_KEY_PREFIX=

# Настройки Rate Limiting
REDIS__RATE_LIMIT__KEY=
REDIS__RATE_LIMIT__LLM_WINDOW=
REDIS__RATE_LIMIT__LLM_LIMIT=
REDIS__RATE_LIMIT__LOCK_TTL=

# === Настройки RabbitMQ ===
RABBITMQ__HOST=
RABBITMQ__PORT=
RABBITMQ__USER=
RABBITMQ__PASSWORD=
RABBITMQ__VHOST=

# === Настройки OpenRouter ===
OPENROUTER__API_KEY=
OPENROUTER__BASE_URL=
OPENROUTER__MODEL=
OPENROUTER__APP_NAME=
OPENROUTER__REFERER=
OPENROUTER__TITLE=
OPENROUTER__REQUEST_TIMEOUT=

# === Настройки CORS ===
CORS__ENABLED=
CORS__ORIGINS=
CORS__METHODS=
CORS__HEADERS=
CORS__CREDENTIALS=

# === Настройки логирования ===
LOGS__FILE_PATH=
LOGS__LEVEL=
LOGS__ROTATION=
```

## Основные настройки

| Параметр   | Тип      | Обязательный | Значение по умолчанию        | Описание                              |
|------------|----------|--------------|------------------------------|---------------------------------------|
| `APP_NAME` | `string` | Нет          | `"Chat API service"`         | Название сервиса                      |
| `ENV`      | `string` | Нет          | `"prod"`                     | Окружение выполнения (prod/dev/test)  |

## Настройки JWT

| Параметр             | Тип       | Обязательный   | Значение по умолчанию | Описание                                                                 |
|----------------------|-----------|----------------|-----------------------|--------------------------------------------------------------------------|
| `JWT__ALG`           | `string`  | Нет            | `"HS256"`             | Алгоритм подписи JWT токенов                                             |
| `JWT__HEADER_NAME`   | `string`  | Нет            | `"Authorization"`     | Имя HTTP заголовка для передачи JWT токена                               |
| `JWT__SECRET__DATA`  | `string`  | Да<sup>*</sup> | `-`                   | Секретный ключ для подписи JWT (в виде строки)<sup>*</sup>               |
| `JWT__SECRET__PATH`  | `string`  | Да<sup>*</sup> | `-`                   | Путь к файлу с секретным ключом для подписи JWT<sup>*</sup>              |

<sup>*</sup> Требуется указать один из параметров: `JWT__SECRET__DATA` или `JWT__SECRET__PATH`. Если указаны оба, будет 
использоваться `JWT__SECRET__DATA`.

## Настройки подключения к БД

| Параметр          | Тип       | Обязательный           | Значение по умолчанию | Описание                                                    |
|-------------------|-----------|------------------------|-----------------------|-------------------------------------------------------------|
| `DB__HOST`        | `string`  | Да                     | `-`                   | Хост базы данных                                            |
| `DB__PORT`        | `integer` | Да                     | `-`                   | Порт базы данных                                            |
| `DB__DB_NAME`     | `string`  | Да                     | `-`                   | Имя базы данных                                             |
| `DB__USER`        | `string`  | Да                     | `-`                   | Пользователь базы данных                                    |
| `DB__PASSWORD`    | `string`  | Да                     | `-`                   | Пароль пользователя базы данных                             |
| `DB__DB_SCHEMA`   | `string`  | Нет                    | `"public"`            | Схема базы данных                                           |
| `DB__DB_TYPE`     | `string`  | Нет                    | `"postgres"`          | Тип базы данных. Допустимые значения: `postgres`, `sqlite`  |
| `DB__TEST_DB_PATH`| `string`  | Условно<sup>**</sup>   | `None`                | Путь к тестовой базе данных SQLite (для `DB_TYPE=sqlite`)   |

<sup>**</sup> Параметр `DB__TEST_DB_PATH` обязателен, если `DB__DB_TYPE=sqlite`.

## Настройки Redis

| Параметр                 | Тип       | Обязательный | Значение по умолчанию       | Описание                                    |
|--------------------------|-----------|--------------|-----------------------------|---------------------------------------------|
| `REDIS__HOST`            | `string`  | Да           | `-`                         | Хост Redis сервера                          |
| `REDIS__PORT`            | `integer` | Да           | `-`                         | Порт Redis сервера                          |
| `REDIS__DB`              | `integer` | Нет          | `0`                         | Номер базы данных Redis                     |
| `REDIS__PASSWORD`        | `string`  | Да           | `-`                         | Пароль для подключения к Redis              |
| `REDIS__TIMEOUT`         | `integer` | Нет          | `30`                        | Таймаут соединения в секундах               |
| `REDIS__CACHE_TTL`       | `integer` | Нет          | `3600`                      | Время жизни кэша в секундах                 |
| `REDIS__IDEM_KEY_PREFIX` | `string`  | Нет          | `"idem:cache"`              | Префикс ключа для идемпотентности           |

### Настройки Rate Limiting

| Параметр                           | Тип       | Обязательный | Значение по умолчанию       | Описание                                      |
|------------------------------------|-----------|--------------|-----------------------------|-----------------------------------------------|
| `REDIS__RATE_LIMIT__KEY`           | `string`  | Нет          | `"rl:llm:requests"`         | Ключ для Rate Limiting                        |
| `REDIS__RATE_LIMIT__LLM_WINDOW`    | `integer` | Нет          | `60`                        | Время окна в секундах                         |
| `REDIS__RATE_LIMIT__LLM_LIMIT`     | `integer` | Нет          | `10`                        | Количество запросов в минуту                  |
| `REDIS__RATE_LIMIT__LOCK_TTL`      | `integer` | Нет          | `300`                       | Время блокировки от дубликатов запросов (сек) |

## Настройки RabbitMQ

| Параметр            | Тип       | Обязательный | Значение по умолчанию | Описание                        |
|---------------------|-----------|--------------|-----------------------|---------------------------------|
| `RABBITMQ__HOST`    | `string`  | Да           | `-`                   | Хост RabbitMQ сервера           |
| `RABBITMQ__PORT`    | `integer` | Да           | `-`                   | Порт RabbitMQ сервера           |
| `RABBITMQ__USER`    | `string`  | Да           | `-`                   | Имя пользователя RabbitMQ       |
| `RABBITMQ__PASSWORD`| `string`  | Да           | `-`                   | Пароль пользователя RabbitMQ    |
| `RABBITMQ__VHOST`   | `string`  | Нет          | `None`                | Виртуальный хост RabbitMQ       |

## Настройки OpenRouter

| Параметр                     | Тип       | Обязательный | Значение по умолчанию                     | Описание                            |
|------------------------------|-----------|--------------|-------------------------------------------|-------------------------------------|
| `OPENROUTER__API_KEY`        | `string`  | Да           | `-`                                       | API ключ для OpenRouter             |
| `OPENROUTER__BASE_URL`       | `string`  | Нет          | `"https://openrouter.ai/api/v1"`          | Базовый URL OpenRouter API          |
| `OPENROUTER__MODEL`          | `string`  | Нет          | `"stepfun/step-3.5-flash:free"`           | Модель OpenRouter по умолчанию      |
| `OPENROUTER__APP_NAME`       | `string`  | Нет          | `"llm-fastapi-openrouter"`                | Заголовок приложения для OpenRouter |
| `OPENROUTER__REFERER`        | `string`  | Да           | `-`                                       | Реферер для OpenRouter              |
| `OPENROUTER__TITLE`          | `string`  | Нет          | `"llm-fastapi-openrouter"`                | Заголовок запроса                   |
| `OPENROUTER__REQUEST_TIMEOUT`| `integer` | Нет          | `10`                                      | Таймаут запроса в секундах          |

## Настройки CORS

| Параметр            | Тип       | Обязательный | Значение по умолчанию | Описание                                        |
|---------------------|-----------|--------------|-----------------------|-------------------------------------------------|
| `CORS__ENABLED`     | `boolean` | Нет          | `true`                | Включение/выключение CORS политики              |
| `CORS__ORIGINS`     | `string`  | Нет          | `"*"`                 | Список разрешенных источников (через запятую)   |
| `CORS__METHODS`     | `string`  | Нет          | `"*"`                 | Список разрешенных HTTP методов (через запятую) |
| `CORS__HEADERS`     | `string`  | Нет          | `"*"`                 | Список разрешенных заголовков (через запятую)   |
| `CORS__CREDENTIALS` | `boolean` | Нет          | `true`                | Разрешить отправку куки/учетных данных          |

## Настройки логирования

| Параметр          | Тип      | Обязательный | Значение по умолчанию    | Описание                                                                      |
|-------------------|----------|--------------|--------------------------|-------------------------------------------------------------------------------|
| `LOGS__FILE_PATH` | `string` | Нет          | `"logs/service.log"`     | Путь к файлу для сохранения логов (может быть относительным или абсолютным)   |
| `LOGS__LEVEL`     | `string` | Нет          | `"INFO"`                 | Уровень логирования. Допустимые значения: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOGS__ROTATION`  | `string` | Нет          | `"1 day"`                | Период ротации логов. Форматы: `"X days"`, `"X hours"`, `"X MB"`, `"X GB"`    |
