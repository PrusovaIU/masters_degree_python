
## Конфигурация

**Шаблон файла .env:**

```
# Основные настройки
APP_NAME=
ENV=
SQLITE_PATH=

# Настройки JWT токенов
JWT__SECRET=
JWT__ALG=
JWT__ACCESS_TOKEN_EXPIRE_MINUTES=

# Настройки подключения к сервису OpenRouter
OPENROUTER__API_KEY=
OPENROUTER__BASE_URL=
OPENROUTER__MODEL=
OPENROUTER__SITE_URL=
OPENROUTER__APP_NAME=
OPENROUTER__REFERER=
OPENROUTER__REQUEST_TIMEOUT=

# Настройки хэширования пароля
PASSWORD__PBKDF2_ITERATIONS=
PASSWORD__SALT_LEN=
PASSWORD__HASH_LEN=

# Настройки CORS
CORS__ENABLED=
CORS__ORIGINS=
CORS__METHODS=
CORS__HEADERS=
CORS__CREDENTIALS=
```
### Основные настройки

<table>
    <thead>
        <tr>
            <th>Название параметра</th>
            <th>Тип значения</th>
            <th>Значение по умолчанию</th>
            <th>Описание</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>APP_NAME</td>
            <td>str</td>
            <td>"llm-p"</td>
            <td>Название приложения</td>
        </tr>
        <tr>
            <td>ENV</td>
            <td>str</td>
            <td>"prod"</td>
            <td>Текущее окружение</td>
        </tr>
        <tr>
            <td>SQLITE_PATH</td>
            <td>str</td>
            <td>"./app.db"</td>
            <td>Путь к файлу SQLite базы данных</td>
        </tr>
    </tbody>
</table>

### Настройки JWT токенов

<table>
    <thead>
        <tr>
            <th>Название параметра</th>
            <th>Тип значения</th>
            <th>Значение по умолчанию</th>
            <th>Описание</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>secret</td>
            <td>str</td>
            <td>—</td>
            <td>Путь к ключу для JWT (обязательный параметр)</td>
        </tr>
        <tr>
            <td>alg</td>
            <td>str</td>
            <td>"HS256"</td>
            <td>Алгоритм подписи JWT токенов</td>
        </tr>
        <tr>
            <td>access_token_expire_minutes</td>
            <td>int</td>
            <td>60</td>
            <td>Время жизни access token в минутах</td>
        </tr>
    </tbody>
</table>

### Настройки подключения к сервису OpenRouter

<table>
    <thead>
        <tr>
            <th>Название параметра</th>
            <th>Тип значения</th>
            <th>Значение по умолчанию</th>
            <th>Описание</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>api_key</td>
            <td>Optional[str]</td>
            <td>—</td>
            <td>API ключ для OpenRouter</td>
        </tr>
        <tr>
            <td>base_url</td>
            <td>str</td>
            <td>"https://openrouter.ai/api/v1"</td>
            <td>Базовый URL OpenRouter API</td>
        </tr>
        <tr>
            <td>model</td>
            <td>str</td>
            <td>"stepfun/step-3.5-flash:free"</td>
            <td>Модель OpenRouter по умолчанию</td>
        </tr>
        <tr>
            <td>site_url</td>
            <td>str</td>
            <td>—</td>
            <td>URL сайта для OpenRouter (обязательный параметр)</td>
        </tr>
        <tr>
            <td>app_name</td>
            <td>Optional[str]</td>
            <td>"llm-fastapi-openrouter"</td>
            <td>Заголовок приложения для OpenRouter</td>
        </tr>
        <tr>
            <td>referer</td>
            <td>Optional[str]</td>
            <td>—</td>
            <td>Referer заголовок для запросов</td>
        </tr>
        <tr>
            <td>request_timeout</td>
            <td>int</td>
            <td>10</td>
            <td>Таймаут запроса в секундах</td>
        </tr>
    </tbody>
</table>

### Настройки хэширования пароля

<table>
    <thead>
        <tr>
            <th>Название параметра</th>
            <th>Тип значения</th>
            <th>Значение по умолчанию</th>
            <th>Описание</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>pbkdf2_iterations</td>
            <td>int</td>
            <td>600000</td>
            <td>Количество итераций для PBKDF2</td>
        </tr>
        <tr>
            <td>salt_len</td>
            <td>int</td>
            <td>32</td>
            <td>Длина соли в байтах</td>
        </tr>
        <tr>
            <td>hash_len</td>
            <td>int</td>
            <td>32</td>
            <td>Длина выходного хеша в байтах</td>
        </tr>
    </tbody>
</table>

### Настройки CORS

<table>
    <thead>
        <tr>
            <th>Название параметра</th>
            <th>Тип значения</th>
            <th>Значение по умолчанию</th>
            <th>Описание</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>enabled</td>
            <td>bool</td>
            <td>True</td>
            <td>Флаг включения CORS</td>
        </tr>
        <tr>
            <td>origins</td>
            <td>list[str]</td>
            <td>["*"]</td>
            <td>Список разрешенных источников</td>
        </tr>
        <tr>
            <td>methods</td>
            <td>list[str]</td>
            <td>["*"]</td>
            <td>Список разрешенных методов</td>
        </tr>
        <tr>
            <td>headers</td>
            <td>list[str]</td>
            <td>["*"]</td>
            <td>Список разрешенных заголовков</td>
        </tr>
        <tr>
            <td>credentials</td>
            <td>bool</td>
            <td>True</td>
            <td>Разрешить отправку куки</td>
        </tr>
    </tbody>
</table>