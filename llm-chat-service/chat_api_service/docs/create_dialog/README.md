# Создание нового диалога

Эндпоинт для создания нового диалга.

## Request

**URL**: `POST /conversation`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**JSON-body**:

| Параметр | Тип | Описание         | Значение по умолчанию | Обязательный  |
|----------|-----|------------------|-----------------------|---------------|
| title    | str | Название диалога | --                    | ✅             |

![request.png](request.png)

**CURL**

```shell
curl -X 'POST' \
  'http://127.0.0.1:8001/conversation/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc2OTQ5MDQ1LCJpYXQiOjE3NzY5NDgxNDUsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.Dr1G7E15YdZ9urUKvuyyF6WIPv17ZJ9ne_cPaGoLtcY' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Новый диалог"
}'
```

## Response

**201 - Created**:

Успешное создание диалога.

| Параметр     | Тип      | Описание                      |
|--------------|----------|-------------------------------|
| id           | UUID     | ID диалога                    |
| title        | str      | Заголовок диалога             |
| created_at   | datetime | Дата и время создания диалога |

![201_CREATED.png](201_CREATED.png)