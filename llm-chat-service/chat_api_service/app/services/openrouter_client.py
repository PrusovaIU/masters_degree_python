import httpx
from loguru import logger

from chat_api_service.app.core.exceptions import openrouter_client as errors
from chat_api_service.app.schemas.config import OpenRouterConfig


class OpenRouterClient:
    """Клиент для работы с OpenRouter API."""
    def __init__(self, settings: OpenRouterConfig):
        self._settings = settings

    def _get_headers(self) -> dict[str, str]:
        """
        Сформировать заголовки для запроса к OpenRouter.

        :return: Заголовки для запроса к OpenRouter.
        """
        return {
            "Authorization": f"Bearer {self._settings.api_key}",
            "HTTP-Referer": self._settings.referer,
            "X-Title": self._settings.title,
            "Content-Type": "application/json"
        }

    async def chat_completion(
            self,
            messages: list[dict[str, str]],
            temperature: float = 0.7,
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
            "model": self._settings.model,
            "messages": messages,
            "temperature": temperature
        }
        try:
            async with httpx.AsyncClient(
                    timeout=self._settings.request_timeout
            ) as client:
                response: httpx.Response = await client.post(
                    f"{self._settings.base_url}/chat/completions",
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
                f"timeout={self._settings.request_timeout}"
            )
        except httpx.HTTPStatusError:
            raise errors.OpenRouterClientException(
                f"Unexpected response status from OpenRouter "
                f"({response.status_code})"
            )
        except httpx.RequestError as err:
            raise errors.OpenRouterClientException(
                f"Connect to OpenRouter error: {err} "
                f"({err.__class__.__name__})"
            )
        return data["choices"][0]["message"]["content"]
