from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_msg_repo_create() -> AsyncMock:
    """
    :return: Мок метода создания сообщения.
    """
    return AsyncMock(name="MessageRepository.create mock")


@pytest.fixture
def mock_msg_repo_update_llm_task_id() -> AsyncMock:
    """
    :return: Мок метода обновления ID задачи LLM
    """
    return AsyncMock(name="MessageRepository.update_llm_task_id mock")


@pytest.fixture
def mock_message_repository(
        mock_msg_repo_create: AsyncMock,
        mock_msg_repo_update_llm_task_id: AsyncMock
) -> AsyncMock:
    """
    Фикстура для создания мока репозитория сообщений

    :param mock_msg_repo_create: Мок метода создания сообщения

    :param mock_msg_repo_update_llm_task_id: Мок метода обновления ID задачи
        LLM.

    :return: Мок репозитория сообщений
    """
    repo = AsyncMock(name="MessageRepository.create mock")
    repo.create = mock_msg_repo_create
    repo.update_llm_task_id = mock_msg_repo_update_llm_task_id
    return repo


@pytest.fixture
def mock_conv_repo_get() -> AsyncMock:
    """
    :return: Мок метода получения диалога.
    """
    return AsyncMock(name="ConversationRepository.get mock")


@pytest.fixture
def mock_conversation_repository(
        mock_conv_repo_get: AsyncMock
) -> AsyncMock:
    """
    Фикстура для мока репозитория диалогов.

    :param mock_conv_repo_get: Мок метода получения диалога.
    :return: Мок репозитория диалогов.
    """
    repo = AsyncMock()
    repo.get = mock_conv_repo_get
    return repo
