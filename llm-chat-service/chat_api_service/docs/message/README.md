# Получение сообщения

Эндпоинт для получения сообщения

## Request

**URL** `GET /conversation/messages/{message_id}`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**Path параметры**

| Параметр   | Тип        | Описание                | Значение по умолчанию | Обязательный  |
|------------|------------|-------------------------|-----------------------|---------------|
| message_id | str (UUID) | Идентификатор сообщения | --                    | ✅             |

![request.png](request.png)

```shell
curl -X 'GET' \
  'http://127.0.0.1:8001/conversation/messages/000af836-6c2c-48aa-8000-34a2a53cd2f7' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzc4MDc4NjA0LCJpYXQiOjE3NzgwNzc3MDQsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.tIEB67dOCLi81KKSwfZV8LVl63u2xC_RShm82K_Rev8'
```

## Response

**200 - OK**:

Сообщение успешно получено

![200_OK.png](200_OK.png)

**403 - Forbidden**

У пользователя нет доступа к сообщению.

![403_FORBIDDEN.png](403_FORBIDDEN.png)

**404 - Not found**

Сообщение с указанным ID не найдено.

![404_NOT_FOUND.png](404_NOT_FOUND.png)