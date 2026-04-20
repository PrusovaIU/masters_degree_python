from os import environ


environ.update({
    "DB__HOST": "localhost",
    "DB__PORT": "5432",
    "DB__DB_NAME": "postgres",
    "DB__USER": "postgres",
    "DB__PASSWORD": "postgres",
    "DB__DB_SCHEMA": "public",

    "REDIS__HOST": "localhost",
    "REDIS__PORT": "6379",
    "REDIS__PASSWORD": "password",

    "RABBITMQ__HOST": "localhost",
    "RABBITMQ__PORT": "5672",
    "RABBITMQ__USER": "guest",
    "RABBITMQ__PASSWORD": "guest",

    "OPENROUTER__API_KEY": "openrouter_api_key",
    "OPENROUTER__REFERER": "openrouter_referer",

    "JWT__SECRET__DATA": "jwt_secret"
})
