# Получение информации о текущем пользователе

Эндпоинт для получения данных профиля аутентифицированного пользователя.

## Request

**URL**: `GET /auth/me`

**Headers**:

| Параметр      | Тип | Описание  | Значение по умолчанию | Обязательный |
|---------------|-----|-----------|-----------------------|--------------|
| Authorization | str | JWT токен | --                    | ✅            |

![request.png](request.png)

**CURL**

```shell
curl -X 'GET' \
  'http://127.0.0.1:8000/auth/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzc1NDAzMjIzLCJpYXQiOjE3NzU0MDIzMjMsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.9VC04ldKxw51v-foPrZMBzAS5mdGMvYGeHvOW2P2vD4'
```

## Response

**200 - OK**

Успешный ответ.

| Параметр   | Тип  | Описание                                                         |
|------------|------|------------------------------------------------------------------|
| id         | int  | ID пользователя                                                  |
| email      | str  | Email пользователя                                               |
| role       | str  | Роль пользователя (всем пользователям присваивается роль `user`) |
| created_at | str  | Дата и время регистрации пользователя                            |
| updated_at | str  | Дата и время изменения пользователя                              |

![200_OK.png](200_OK.png)

**401 - Unauthorized**

Не передан заголовок с access токеном, или токен навалиден.

![401_UNAUTHORIZED.png](401_UNAUTHORIZED.png)