# Запуск проекта

## 1. Настройка виртуального окружения

`uv` — это быстрый менеджер пакетов и инструмент для управления виртуальными окружениями. 
Если uv еще не установлен, установите его с помощью команды:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Инициализация виртуального окружения

Создайте и синхронизируйте виртуальное окружение с зависимостями проекта:

```shell
uv sync
```

Эта команда создаст виртуальное окружение и установит все зависимости, указанные в `pyproject.toml`.

## 2. Запуск сервера

Запустите сервер с помощью команды:

```shell
 uv run uvicorn web_service.app.main:app --reload --host 0.0.0.0 --port 8002 --env-file .env
```

**Параметры запуска**

| Параметр | Описание                        | Значение по умолчанию |
|----------|---------------------------------|-----------------------|
| host     | Хост сервера                    | 127.0.0.1             |
| port     | Порт сервера                    | 8000                  |
| env-file | Путь к файла с настройками      | -                     |

При успешном запуске в терминале появятся логи, аналогичные следующим:

```shell
INFO:     Will watch for changes in these directories: ['/home/hex/git/masters_degree_python/llm-chat-service']
INFO:     Loading environment from '/home/hex/git/masters_degree_python/llm-chat-service/web_service/.env'
INFO:     Uvicorn running on http://0.0.0.0:8002 (Press CTRL+C to quit)
INFO:     Started reloader process [307132] using StatReload
INFO:     Started server process [307134]
INFO:     Waiting for application startup.
2026-05-07 11:32:33.201 | SUCCESS  | web_service.app.infra.rabbitmq:connect:24 - Подключено к RabbitMQ: amqp://admin:123456@127.0.0.1:5672
INFO:     Application startup complete.
```

После запуска сервера перейдите в браузере по хосту `http://localhost:8002`:

![start_page.png](imgs/start_page.png)