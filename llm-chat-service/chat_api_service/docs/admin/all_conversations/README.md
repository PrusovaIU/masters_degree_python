# Список всех диалогов

Эндпоинт для списка всех диалогов.

**Доступен только для пользователей с ролью `admin`**.

## Request:

**URL**: `GET /admin/conversations/all`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**JSON-body**:

| Параметр | Тип | Описание                         | Значение по умолчанию | Обязательный |
|----------|-----|----------------------------------|-----------------------|--------------|
| limit    | int | Количество элементов на странице | 20                    | ❌            |
| offset   | int | Смещение пагинации               | 0                     | ❌            | 

![request.png](request.png)

**CURL**

```shell
curl -X 'POST' \
  'http://127.0.0.1:8001/admin/conversations/all' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc3MTQyNjg3LCJpYXQiOjE3NzcxNDE3ODcsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoiYWRtaW4ifQ.Yck4-9GyuuhMGubxVfzqwakhkXH0kgIBx2zhcgTbKog' \
  -H 'Content-Type: application/json' \
  -d '{
  "limit": 20,
  "offset": 0
}'
```

## Response

**200 - OK**:

Список сообщений получен успешно. Сообщения отсортированы по времени создания (по убыванию).

![200_OK.png](200_OK.png)

**403 - Forbidden**

Если запрос сделан пользователем без роли `admin`.

![403_FORBIDDEN.png](403_FORBIDDEN.png)