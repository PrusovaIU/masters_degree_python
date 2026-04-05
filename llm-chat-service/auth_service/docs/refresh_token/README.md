# Обновление access токена

Эндпоинт для обновления access токена через refresh токен.

## Request

**URL**: `POST /auth/refresh`

**JSON-body**:

| Параметр      | Тип     | Описание      | Значение по умолчанию | Обязательный |
|---------------|---------|---------------|-----------------------|--------------|
| refresh_token | string  | Refresh токен | --                    | ✅            |

![request.png](request.png)

**CURL**

```shell
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/refresh' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzc1NDg5MzM4LCJpYXQiOjE3NzU0MDI5MzgsInR5cGUiOiJyZWZyZXNoIn0.SxpW8G_Ie9767WTPwWQUUXzYrHQvsC44gjrVcnMzJ6U"
}'
```

## Response

**200 - OK**:

Успешный ответ.

| Параметр           | Тип | Описание                              |
|--------------------|-----|---------------------------------------|
| access_token       | str | Access токен                          |
| expires_in         | int | Время жизни access токен в секундах   |
| token_type         | str | Тип токена                            |

![200_OK.png](200_OK.png)

**401 - Unauthorized**:

Указан невалидный refresh токен.

![401_UNAUTHORIZED.png](401_UNAUTHORIZED.png)
