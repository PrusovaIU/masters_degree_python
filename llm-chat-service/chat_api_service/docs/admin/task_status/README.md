# Получение статуса задачи обработки запроса к LLM

Эндпоинт для получения статуса задач обработки запросок к LLM по ID задачи. 

**Доступен только для пользователей с ролью `admin`**.

## Request:

**URL**: `GET /admin/tasks/{task_id}/status`

**Headers**:

| Параметр      | Тип | Описание                      | Значение по умолчанию | Обязательный  |
|---------------|-----|-------------------------------|-----------------------|---------------|
| Authorization | str | Авторизация по схеме `Bearer` | --                    | ✅             |

**Path параметры**

| Параметр | Тип        | Описание             | Значение по умолчанию | Обязательный |
|----------|------------|----------------------|-----------------------|--------------|
| task_id  | str (uuid) | Идентификатор задачи | --                    | ✅            |

![request.png](request.png)

**CURL**

```shell
curl -X 'GET' \
  'http://127.0.0.1:8001/admin/tasks/08e431c1-494b-4799-bcc9-dbc10ca9cb50/status' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc3MTM4MDU3LCJpYXQiOjE3NzcxMzcxNTcsInR5cGUiOiJhY2Nlc3MiLCJyb2xlIjoiYWRtaW4ifQ.kO7rPMnKuQp5oiSQIvbHCVWMBNuuY9LbidKh6d8yVc4'
```

## Response:

**200 - OK**

Задача найдена:

![200_OK.png](200_OK.png)

Задача не найдена или еще не начала выполняться:

![200_OK_PENDING.png](200_OK_PENDING.png)

**403 - Forbidden**

Если запрос сделан пользователем без роли `admin`.

![403_FORBIDDEN.png](403_FORBIDDEN.png)
