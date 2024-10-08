import asyncio
import uuid
from typing import Union

import pytest
from taskiq import AckableMessage, AsyncBroker, BrokerMessage

from taskiq_sqs import SQSBroker


def test_no_url_should_raise_typeerror() -> None:
    """Test that url is expected."""
    with pytest.raises(TypeError):
        SQSBroker()  # type: ignore


async def get_message(
    broker: AsyncBroker,
) -> Union[bytes, AckableMessage]:
    """
    Get a message from the broker.

    :param broker: async message broker.
    :return: first message from listen method.
    """
    async for message in broker.listen():
        return message
    return b""


@pytest.fixture
def valid_broker_message() -> BrokerMessage:
    """
    Generate valid broker message for tests.

    :returns: broker message.
    """
    return BrokerMessage(
        task_id=uuid.uuid4().hex,
        task_name=uuid.uuid4().hex,
        message=b"my_msg",
        labels={
            "label1": "val1",
        },
    )


@pytest.mark.anyio
async def test_sqs_broker(
    valid_broker_message: BrokerMessage,
    sqs_queue_url: str,
) -> None:
    """
    Test that messages are published and read correctly by SQSBroker.

    We create two workers that listen and send a message to them.
    Expect both workers to receive the same message we sent.
    """
    broker = SQSBroker(queue_url=sqs_queue_url, aws_region="us-east-1")

    await broker.kick(valid_broker_message)
    await asyncio.sleep(0.3)

    message1 = await broker.listen().__anext__()
    assert message1.data == valid_broker_message.message
    await broker.shutdown()
