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
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 --env-file .env
```


**Параметры запуска**

| Параметр | Описание                        | Значение по умолчанию |
|----------|---------------------------------|-----------------------|
| host     | Хост сервера                    | 127.0.0.1             |
| port     | Порт сервера                    | 8000                  |
| env-file | Путь к файла с настройками      | -                     |

При успешном запуске в терминале появятся логи, аналогичные следующим:

```shell
INFO:     Started server process [162550]
INFO:     Waiting for application startup.
2026-04-23 14:40:56.099 | INFO     | chat_api_service.app.infra.redis:setup:31 - Redis клиент инициализирован.
2026-04-23 14:40:56.124 | INFO     | chat_api_service.app.db.session:setup:60 - Инициализация класса DBSession завершена.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     127.0.0.1:51516 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:51516 - "GET /openapi.json HTTP/1.1" 200 OK
```


После запуска сервера перейдите в браузере по хосту `http://localhost:8001/docs`:

![openapi.png](imgs/openapi.png)