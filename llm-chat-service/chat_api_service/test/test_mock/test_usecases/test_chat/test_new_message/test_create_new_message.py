from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest
from pytest_mock import MockerFixture

from chat_api_service.app.db.models import Message
from chat_api_service.app.usecases.chat import new_message
from libs.consts.llm_tasks import LLMTasksStatus
from libs.consts.message import MessageStatus, SenderType
from libs.schemas.llm_query import LLMQueryRequest, LLMQueryResponse

USER_ID = "test_user_123"
CONVERSATION_ID = uuid4()
CONTENT = "Hello, how are you?"
IDEMPOTENCY_KEY = "idem:test_key_123"


@pytest.fixture
def user_request() -> LLMQueryRequest:
    """
    :return: Тестовый запрос на создание сообщения
    """
    return LLMQueryRequest(
        conversation_id=CONVERSATION_ID,
        content=CONTENT,
        temperature=0.8
    )


@pytest.fixture
def created_message():
    """
    :return: Тестовое сообщение созданное в БД.
    """
    return Message(
        id=uuid4(),
        conversation_id=CONVERSATION_ID,
        content=CONTENT,
        sender_type=SenderType.USER,
        status=MessageStatus.SENT,
        idempotency_key="idem:test_key_123",
        llm_task_id=None,
        created_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_llm_task() -> MagicMock:
    """
    :return: Тестовая Celery задача.
    """
    task = MagicMock()
    task.id = "celery_task_123"
    return task


@pytest.fixture
def new_message_usecase(
        mock_message_repository,
        mock_conversation_repository,
        user_request: LLMQueryRequest
) -> new_message.NewMessageUsecase:
    """
    :param mock_message_repository: Мок репозитория сообщений.
    :param mock_conversation_repository: Мок репозитория диалогов.
    :param user_request: Тестовый запрос на создание сообщения.
    :return: Usecase создания нового сообщения.
    """
    usecase = new_message.NewMessageUsecase(
        message_repository=mock_message_repository,
        conversation_repository=mock_conversation_repository,
        user_id=USER_ID,
        user_request=user_request,
        custom_idem_key=IDEMPOTENCY_KEY
    )
    return usecase


@pytest.fixture
def mock_llm_request_delay() -> Mock:
    """
    :return: Мок метода отправки запроса в очередь.
    """
    return Mock(name="llm_request.delay mock")


@pytest.fixture
def mock_llm_request(
        mocker: MockerFixture,
        mock_llm_request_delay: AsyncMock
) -> Generator[AsyncMock, None, None]:
    """
    :param mocker: Фикстура pytest-mocker.
    :param mock_llm_request_delay: Мок метода отправки запроса в очередь.
    :return: Мок метода отправки запроса в LLM.
    """
    mock = mocker.patch.object(
        new_message,
        "llm_request",
        name="llm_request mock"
    )
    mock.delay = mock_llm_request_delay
    yield mock


@pytest.mark.asyncio
async def test_create_new_message_success(
        new_message_usecase: new_message.NewMessageUsecase,
        mock_message_repository: AsyncMock,
        mock_msg_repo_create: AsyncMock,
        mock_conversation_repository: AsyncMock,
        mock_conv_repo_get: AsyncMock,
        created_message: Message,
        mock_llm_request: AsyncMock,
        mock_llm_request_delay: AsyncMock,
        mock_llm_task: MagicMock,
        user_request: LLMQueryRequest
):
    """
    Тест успешного создания нового сообщения.

    :param new_message_usecase: Usecase создания нового сообщения.

    :param mock_message_repository: Мок репозитория сообщений.

    :param mock_msg_repo_create: Мок метода создания сообщения в репозитории
        сообщений.

    :param mock_conversation_repository: Мок репозитория диалогов.

    :param mock_conv_repo_get: Мок метода получения диалога из репозитория.

    :param created_message: Тестовое сообщение созданное в БД.

    :param mock_llm_request: Мок метода отправки запроса в LLM.

    :param mock_llm_request_delay: Мок метода отправки запроса в очередь.

    :param mock_llm_task: Тестовая Celery задача.

    :param user_request: Тестовый запрос на создание сообщения.
    """
    mock_conv_repo_get.return_value = MagicMock()
    mock_msg_repo_create.return_value = created_message
    mock_llm_request_delay.return_value = mock_llm_task

    result: LLMQueryResponse = await new_message_usecase._create_new_message()

    mock_conv_repo_get.assert_called_once_with(
        CONVERSATION_ID,
        USER_ID
    )

    # Проверка вызова создания сообщения
    mock_msg_repo_create.assert_called_once()
    create_call_args = mock_msg_repo_create.call_args[1]
    assert create_call_args['conversation_id'] == CONVERSATION_ID
    assert create_call_args['message_in'].sender_type == SenderType.USER
    assert create_call_args['message_in'].content == CONTENT
    assert create_call_args['message_in'].status == MessageStatus.SENT
    assert create_call_args['idempotency_key'] == IDEMPOTENCY_KEY

    # Проверка запуска Celery задачи
    mock_llm_request_delay.assert_called_once_with(
        message_id=str(created_message.id),
        conversation_id=str(CONVERSATION_ID),
        content=CONTENT,
        idempotency_key=IDEMPOTENCY_KEY,
        temperature=user_request.temperature,
        user_id=USER_ID
    )

    # Проверка обновления task_id
    mock_message_repository.update_llm_task_id.assert_called_once_with(
        created_message.id,
        mock_llm_task.id
    )

    # Проверка возвращаемого ответа
    assert result.message_id == created_message.id
    assert result.task_id == mock_llm_task.id
    assert result.status == LLMTasksStatus.QUEUED
    assert result.conversation_id == CONVERSATION_ID
