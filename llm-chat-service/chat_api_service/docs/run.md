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
uv run uvicorn chat_api_service.app.main:app --reload --host 0.0.0.0 --port 8001 --env-file .env
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

## 3. Запуск Celery

```shell
celery -A chat_api_service.app.infra.celery_app:celery_app worker     --loglevel=info     --concurrency=100     --pool=custom
```
При успешном запуске в терминале появятся логи, аналогичные следующим:

```shell
amqp://admin:123456@127.0.0.1:5672
2026-04-24 19:35:19.614 | INFO     | chat_api_service.app.db.session:setup:73 - Инициализация класса DBSession завершена.
/home/hex/git/masters_degree_python/llm-chat-service/chat_api_service/app/tasks/llm_tasks.py:26: RuntimeWarning: coroutine 'RedisClient.setup' was never awaited
  RedisClient.setup(settings.redis)
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
[2026-04-24 19:35:19,631: WARNING/MainProcess] /home/hex/git/masters_degree_python/llm-chat-service/.venv/lib/python3.13/site-packages/celery_aio_pool/__init__.py:30: UserWarning: Replacing Celery's default `build_tracer` utility w/ `build_async_tracer` from celery-aio-pool
  celery.app.trace.warn(

 
 -------------- celery@fox v5.3.1 (emerald-rush)
--- ***** -----                                                                                                                             
-- ******* ---- Linux-6.8.0-107-generic-x86_64-with-glibc2.35 2026-04-24 19:35:19                                                           
- *** --- * ---                                                                                                                             
- ** ---------- [config]                                                                                                                    
- ** ---------- .> app:         chat_api_service:0x7242d6218050                                                                             
- ** ---------- .> transport:   amqp://admin:**@127.0.0.1:5672//                                                                            
- ** ---------- .> results:     redis://:**@127.0.0.1:6379/1                                                                                
- *** --- * --- .> concurrency: 100 (pool)                                                                                                  
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)                                                             
--- ***** -----                                                                                                                             
 -------------- [queues]                                                                                                                    
                .> celery           exchange=celery(direct) key=celery                                                                      
                                                                                                                                            
                                                                                                                                            
[tasks]
  . chat_api_service.llm_request

[2026-04-24 19:35:19,671: INFO/MainProcess] Connected to amqp://admin:**@127.0.0.1:5672//
[2026-04-24 19:35:19,677: INFO/MainProcess] mingle: searching for neighbors
[2026-04-24 19:35:20,717: INFO/MainProcess] mingle: all alone
[2026-04-24 19:35:20,768: INFO/MainProcess] celery@fox ready.
```
