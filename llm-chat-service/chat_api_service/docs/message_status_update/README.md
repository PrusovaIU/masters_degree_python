# Обновление статуса сообщения

Эндпоинт для обновления статуса сообщения.

## Request:

**URL**: `POST /conversation/messages/{message_id}/status`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**Path параметры**

| Параметр   | Тип        | Описание                | Значение по умолчанию | Обязательный |
|------------|------------|-------------------------|-----------------------|--------------|
| message_id | str (uuid) | Идентификатор сообщения | --                    | ✅            |

**JSON-body**:

| Параметр | Тип | Описание                            | Значение по умолчанию | Обязательный |
|----------|-----|-------------------------------------|-----------------------|--------------|
| status   | str | Новый статус сообщения <sub>*</sub> | --                    | ✅            |

<sub>*</sub> Доступные статусы: 
* sent - отправлен;
* processing - обрабатывается;
* delivered - доставлено получателю;
* read - прочитано пользователем;
* failed - ошибка обработки.

*Разрешенные переходы:*

![status_update.png](status_update.png)

![request.png](request.png)

**CURL**

```shell
curl -X 'PATCH' \
  'http://127.0.0.1:8001/conversation/messages/79b13865-10d9-4a25-8630-26359d709a7a/status' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc3MDQ2NDA3LCJpYXQiOjE3NzcwNDU1MDcsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoidXNlciJ9.NYo7P_n6c1aP8Ilo_Bkb-eZYOuEFzCfe2fwSYIUO8nk' \
  -H 'Content-Type: application/json' \
  -d '{
  "status": "read"
}'
```

## Response:

**200 - OK**

Статус успешно обновлен.

![200_OK.png](200_OK.png)

**400 - Bad request**

Невалидный переход между статусами.

![400_BAD_REQUEST.png](400_BAD_REQUEST.png)

**403 - Forbidden**

У пользователя нет доступа к сообщению.

![403_FORBIDDEN.png](403_FORBIDDEN.png)

**404 - Not found**

Сообщение с указанным ID не найдено.

![404_NOT_FOUND.png](404_NOT_FOUND.png)