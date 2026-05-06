# История диалога до определенного сообщения

Эндпоинт для получения списка сообщений из диалога.

## Request

**URL** `GET /conversation/history`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**Query параметры**

| Параметр          | Тип        | Описание                                             | Значение по умолчанию | Обязательный |
|-------------------|------------|------------------------------------------------------|-----------------------|--------------|
| conversation_id   | str (UUID) | Идентификатор диалога                                | --                    | ✅            |
| before_message_id | str (UUID) | Идентификатор сообщения, до которого вывести историю | --                    | ✅            |
| limit             | int        | Количество записей для вывода                        | 10                    | ❌            |

![request.png](request.png)

**CURL**
```shell
curl -X 'GET' \
  'http://127.0.0.1:8001/conversation/history/before?conversation_id=434fc00a-2955-4a96-a4f9-b42d7be33ead&before_message_id=c45e6da0-9a0f-4501-8c99-418632920ee5&limit=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc4MDg5MzI1LCJpYXQiOjE3NzgwODg0MjUsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoiYWRtaW4ifQ.iuTuDL6EIWWL5GoV1JxnKL4SFYZp-56Q9U9JCt44xB4'
```

## Response

**200 - OK**:

Список сообщений получен успешно. Сообщения отсортированы по времени создания (по убыванию).

![200_OK.png](200_OK.png)

**403 - Forbidden**

Диалог принадлежит другому пользователю

![403_FORBIDDEN.png](403_FORBIDDEN.png)

**404 - Not found**

Диалог с указанным идентификатором не найден.

![404_NOT_FOUND.png](404_NOT_FOUND.png)