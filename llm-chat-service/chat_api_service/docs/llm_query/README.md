# Запрос к LLM

Эндпоинт для отправки пользовательского запроса LLM.

В процессе выполнения запроса сообщение пользователя вносится в базу данных и создается задача для 
[celery](../celery/README.md).

## Request:[README.md](../celery/README.md)

**URL**: `POST /conversation/all`

**Headers**:

| Параметр          | Тип | Описание                              | Значение по умолчанию | Обязательный  |
|-------------------|-----|---------------------------------------|-----------------------|---------------|
| Authorization     | str | Авторизация по схеме `Bearer`         | --                    | ✅             |
| X-Idempotency-Key | str | Пользовательский ключ идемпотентности | None                  | ❌             |

**JSON-body**:

| Параметр        | Тип   | Описание                                                                  | Значение по умолчанию | Обязательный |
|-----------------|-------|---------------------------------------------------------------------------|-----------------------|--------------|
| conversation_id | UUID  | Идентификатор диалога                                                     | -                     | ✅            |
| content         | str   | Текст сообщения пользователя                                              | -                     | ✅            |
| temperature     | float | Параметр креативности (0.0 — детерминировано, 2.0 — максимально случайно) | -                     | ✅            |

![request.png](request.png)

**CURL**

```shell
curl -X 'POST' \
  'http://127.0.0.1:8001/chat/llm/query' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc3MTE4MTYzLCJpYXQiOjE3NzcxMTcyNjMsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.fQ-qVsVKgzYiwJRd-gLALBXQC7KovxMrzBISJLhwgJw' \
  -H 'Content-Type: application/json' \
  -d '{
  "conversation_id": "4fb3df18-290b-46f6-83bb-b1f0bfd4e1f1",
  "content": "Найди самое близкое простое число",
  "temperature": 0.7
}'
```

## Response:

**202 - Accepted**:

![202_ACCEPTED.png](202_ACCEPTED.png)

**403 - Forbidden**

Диалог принадлежит другому пользователю

![403_FORBIDDEN.png](403_FORBIDDEN.png)

**404 - Not found**

Диалог с указанным идентификатором не найден.

![404_NOT_FOUND.png](404_NOT_FOUND.png)
