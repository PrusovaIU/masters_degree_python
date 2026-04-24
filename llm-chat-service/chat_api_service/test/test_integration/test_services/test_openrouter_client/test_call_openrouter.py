import json

import pytest
import respx
from httpx import Response


@respx.mock
@pytest.mark.asyncio
async def test_call_openrouter_success(openrouter_client, openrouter_config):
    """
    Тест успешного вызова OpenRouter API.
    Проверяет формирование payload, заголовков и извлечение ответа.
    """
    test_messages = [
        {"role": "user", "content": "Привет, как дела?"},
        {"role": "assistant", "content": "Всё отлично!"},
        {"role": "user", "content": "Расскажи шутку"},
    ]
    test_temperature = 0.8
    expected_response = "Шутка дня"

    # Мок-ответ от OpenRouter
    mock_response_payload = {
        "id": "test-response-id",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": expected_response,
                },
                "finish_reason": "stop",
            }
        ],
        "model": openrouter_config.model,
        "usage": {"prompt_tokens": 42, "completion_tokens": 18,
                  "total_tokens": 60},
    }
    route = respx.post(
        f"{openrouter_config.base_url}/chat/completions"
    ).mock(
        return_value=Response(
            status_code=200,
            json=mock_response_payload,
        )
    )

    result = await openrouter_client.call_openrouter(
        messages=test_messages,
        temperature=test_temperature,
    )

    # Проверяем, что запрос был сделан
    assert route.called
    assert route.call_count == 1

    # Проверяем заголовки запроса
    request = route.calls.last.request
    assert (request.headers["Authorization"]
            == f"Bearer {openrouter_config.api_key}")
    assert request.headers["HTTP-Referer"] == openrouter_config.referer
    assert request.headers["X-Title"] == openrouter_config.title
    assert request.headers["Content-Type"] == "application/json"

    # Проверяем payload запроса
    payload = json.loads(request.content)
    assert payload["model"] == openrouter_config.model
    assert payload["messages"] == test_messages
    assert payload["temperature"] == test_temperature
    assert result == expected_response
