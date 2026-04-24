# Список диалогов

Эндпоинт для получения списка диалогов текущего пользователя.

## Request:

**URL**: `POST /conversation/all`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**JSON-body**:

| Параметр | Тип | Описание                         | Значение по умолчанию | Обязательный |
|----------|-----|----------------------------------|-----------------------|--------------|
| limit    | int | Количество элементов на странице | 20                    | ❌            |
| offset   | int | Смещение                         | 0                     | ❌            |

![request.png](request.png)

**CURL**

```shell
curl -X 'POST' \
  'http://127.0.0.1:8001/conversation/all' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc3MDI0ODMwLCJpYXQiOjE3NzcwMjM5MzAsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.bqAZ3Uhmn-d-kxYoOmMzLI9hjuSZpovtkVa0llNM7ZI' \
  -H 'Content-Type: application/json' \
  -d '{
  "limit": 20,
  "offset": 0
}'
```

## Response:

**200 - OK**:

![200_OK.png](200_OK.png)