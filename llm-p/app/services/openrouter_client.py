import httpx

from app.core.config import settings
from app.core.errors import openrouter_client as errors
from loguru import logger

from app.core.errors.openrouter_client import OpenRouterClientException


class OpenRouterClient:
    """Клиент для работы с OpenRouter API."""

    @staticmethod
    def _get_headers() -> dict[str, str]:
        """Сформировать заголовки для запроса к OpenRouter."""
        return {
            "Authorization": f"Bearer {settings.openrouter.api_key}",
            "HTTP-Referer": settings.openrouter_referer,
            "X-Title": settings.openrouter_title,
            "Content-Type": "application/json"
        }

    async def chat_completion(
            self,
            messages: list[dict[str, str]],
            temperature: float = 0.7
    ) -> str:
        """
        Отправить запрос к OpenRouter API.

        :param messages: Список сообщений в формате
            [{"role": "...", "content": "..."}]

        :param temperature: Параметр температуры (креативности)

        :return str: Текст ответа модели

        :raises OpenRouterClientException: При ошибке запроса к API
        """
        payload = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": temperature
        }
        try:
            async with httpx.AsyncClient(
                    timeout=settings.openrouter.request_timeout
            ) as client:
                response: httpx.Response = await client.post(
                    f"{settings.openrouter.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
        except (KeyError, IndexError) as err:
            logger.error(f"Unexpected response from OpenRouter: "
                         f"{err} ({err.__class__.__name__})")
            raise errors.UnexpectedResponseException(err)
        except httpx.TimeoutException:
            logger.error("Connect to OpenRouter timed out")
            raise errors.TimeoutException(
                f"timeout={settings.openrouter.request_timeout}"
            )
        except httpx.HTTPStatusError:
            raise errors.OpenRouterClientException(
                f"Unexpected response status from OpenRouter "
                f"({response.status_code})"
            )
        except httpx.RequestError as err:
            raise OpenRouterClientException(
                f"Connect to OpenRouter error: {err} "
                f"({err.__class__.__name__})"
            )
        return data["choices"][0]["message"]["content"]
