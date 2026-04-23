# Список диалогов

Эндпоинт для получения списка диалогов текущего пользователя.

## Request:

**URL**: `GET /conversation/all`

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
curl -X 'GET' \
  'http://127.0.0.1:8001/conversation/all?limit=20&offset=0' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc2OTQ5NzA4LCJpYXQiOjE3NzY5NDg4MDgsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.VjkxwVEWNd-YAyjveqOxRAuuZPoAZvKm6NiSdLRq5h8'
```

## Response:

**200 - OK**:

![200_OK.png](200_OK.png)