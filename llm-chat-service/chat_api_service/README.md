# Chat API service

Микросервис для управления чатами с интеграцией больших языковых моделей (LLM) через OpenRouter API. Предоставляет 
REST API для создания диалогов, отправки сообщений, асинхронной обработки запросов к ИИ и отслеживания статусов.

---

## Содержание

1. [Конфигурация](docs/config.md);
2. [Запуск](docs/run.md);
3. [Создание нового диалога](docs/create_conversation/README.md);
4. [Список диалогов](docs/list_conversation/README.md);
5. [История диалога](docs/conversation_history/README.md);
6. [История диалога до определенного сообщения](docs/conversation_history_before/README.md)
7. [Сведения о диалоге](docs/conversation_info/README.md);
8. [Получение сообщения](docs/message/README.md);
9. [Обновление статуса сообщения](docs/message_status_update/README.md);
10. [Запрос LLM](docs/llm_query/README.md);
11. [[ADMIN] Получение статуса задачи](docs/admin/task_status/README.md);
12. [[ADMIN] Получение списка всех диалогов](docs/admin/all_conversations/README.md);
13. [Задача Celery](docs/celery/README.md);
14. [Тестирование](docs/tests/README.md);
15. [Health check](docs/health/README.md).