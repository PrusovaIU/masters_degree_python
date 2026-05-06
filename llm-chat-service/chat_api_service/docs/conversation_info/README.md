# Сведения о диалоге

Эндпоинт для получения сведений о диалоге

## Request

**URL** `GET /conversation/history`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**Query параметры**

| Параметр        | Тип        | Описание              | Значение по умолчанию | Обязательный  |
|-----------------|------------|-----------------------|-----------------------|---------------|
| conversation_id | str (UUID) | Идентификатор диалога | --                    | ✅             |

![request.png](request.png)

**CURL:**

```shell
curl -X 'GET' \
  'http://127.0.0.1:8001/conversation/info?conversation_id=30f278a6-a07c-414c-b2f4-7f1ec0da7dbd' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc4MDcxMDI0LCJpYXQiOjE3NzgwNzAxMjQsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoiYWRtaW4ifQ.sPT4S9hxtsxO_Aj2tZMyva4E1F4_ARmjxWc2aa-PMuk'
```


## Response

**200 - OK**:

Сведения о диалоге успешно получены

![200_OK.png](request.png)

**403 - Forbidden**

Диалог принадлежит другому пользователю

![403_FORBIDDEN.png](403_FORBIDDEN.png)

**404 - Not found**

Диалог с указанным идентификатором не найден.

![404_NOT_FOUND.png](404_NOT_FOUND.png)