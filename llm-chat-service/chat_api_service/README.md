# Chat API service

Микросервис для управления чатами с интеграцией больших языковых моделей (LLM) через OpenRouter API. Предоставляет 
REST API для создания диалогов, отправки сообщений, асинхронной обработки запросов к ИИ и отслеживания статусов.

---

## Содержание

1. [Конфигурация](docs/config.md);
2. [Запуск](docs/run.md);
3. [Создание нового диалога](docs/create_conversation/README.md);
4. [Список диалогов](docs/list_conversation/README.md);
5. [Список сообщений диалога](docs/conversation_history/README.md);
6. [Сведения о диалоге](docs/conversation_info/README.md);
7. [Получение сообщения](docs/message/README.md);
8. [Обновление статуса сообщения](docs/message_status_update/README.md);
9. [Запрос LLM](docs/llm_query/README.md);
10. [[ADMIN] Получение статуса задачи](docs/admin/task_status/README.md);
11. [[ADMIN] Получение списка всех диалогов](docs/admin/all_conversations/README.md);
12. [Задача Celery](docs/celery/README.md);
13. [Тестирование](docs/tests/README.md);
14. [Health check](docs/health/README.md).