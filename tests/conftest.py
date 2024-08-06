import os

import pytest


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Anyio backend.

    Backend for anyio pytest plugin.
    :return: backend name.
    """
    return "asyncio"


@pytest.fixture
def sqs_queue_url() -> str:
    """
    URL to connect to redis.

    It tries to get it from environ,
    and return default one if the variable is
    not set.

    :return: URL string.
    """
    return os.environ.get(
        "TEST_SQS_QUEUE_URL",
        "http://localhost:4566/000000000000/Queue",
    )
