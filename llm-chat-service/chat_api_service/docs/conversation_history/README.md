# История диалога

Эндпоинт для получения списка сообщений из диалога.

## Request

**URL** `POST /conversation/history`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**Query параметры**

| Параметр        | Тип        | Описание              | Значение по умолчанию | Обязательный  |
|-----------------|------------|-----------------------|-----------------------|---------------|
| conversation_id | str (UUID) | Идентификатор диалога | --                    | ✅             |

**JSON-body**:

| Параметр | Тип | Описание                         | Значение по умолчанию | Обязательный |
|----------|-----|----------------------------------|-----------------------|--------------|
| limit    | int | Количество элементов на странице | 20                    | ❌            |
| offset   | int | Смещение пагинации               | 0                     | ❌            | 

![request.png](request.png)

**CURL**

```shell
curl -X 'POST' \
  'http://127.0.0.1:8001/conversation/history?conversation_id=4fb3df18-290b-46f6-83bb-b1f0bfd4e1f1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc3MDI0ODMwLCJpYXQiOjE3NzcwMjM5MzAsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.bqAZ3Uhmn-d-kxYoOmMzLI9hjuSZpovtkVa0llNM7ZI' \
  -H 'Content-Type: application/json' \
  -d '{
  "limit": 20,
  "offset": 0
}'
```

## Response

**200 - OK**:

Список сообщений получен успешно. Сообщения отсортированы по времени создания (по убыванию).

| Параметр           | Тип        | Описание          |
|--------------------|------------|-------------------|
| conversation_id    | UUID       | ID диалога        |
| conversation_title | str        | Заголовок диалога |
| messaged           | list[dict] | Список сообщений  |
| pagination         | dict       | Данные пагинации  |  

*Message*:

| Параметр        | Тип      | Описание                          |
|-----------------|----------|-----------------------------------|
| id              | UUID     | ID сообщения                      |
| conversation_id | UUID     | ID диалога                        |
| content         | str      | Тест сообщения                    |
| status          | str      | Статус сообщения                  |
| created_at      | datetime | Дата и время создания сообщения   |
| updated_at      | datetime | Дата и время обновления сообщения |
| metadata_json   | dict     | Дополнительные данные             |

*Pagination*:

| Параметр | Тип | Описание                                   |
|----------|-----|--------------------------------------------|
| limit    | int | Запрошенное количество записей на странице |
| offset   | int | Запрошенное смещение                       |
| total    | int | Общее количество записей                   |

![200_OK.png](200_OK.png)

**404 - Not found**

Диалог с указанным идентификатором не найден.

![404_NOT_FOUND.png](404_NOT_FOUND.png)
