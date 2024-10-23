import base64
import json
from logging import getLogger
from typing import AsyncGenerator, Callable, Optional, TypeVar

from aiobotocore.client import AioBaseClient
from aiobotocore.session import AioSession, get_session
from taskiq import AckableMessage, AsyncBroker, BrokerMessage
from taskiq.abc.result_backend import AsyncResultBackend

_T = TypeVar("_T")

logger = getLogger("taskiq.sqs_broker")


class SQSBroker(AsyncBroker):
    """Broker for AWS SQS, manages sending, receiving, encoding, and acknowledgment."""

    def __init__(
        self,
        queue_url: str,
        aws_region: str,
        max_messages: int = 10,
        wait_time: int = 20,
        task_id_generator: Optional[Callable[[], str]] = None,
        result_backend: Optional[AsyncResultBackend[_T]] = None,
    ) -> None:
        super().__init__(
            result_backend=result_backend,
            task_id_generator=task_id_generator,
        )
        self.queue_url = queue_url
        self.max_messages = max_messages
        self.wait_time = wait_time
        self.session: AioSession = get_session()
        self.aws_region = aws_region

    async def shutdown(self) -> None:
        """Shuts down broker and cleans resources, calling superclass cleanup method.

        Returns:
            None
        """
        await super().shutdown()

    async def kick(self, message: BrokerMessage) -> None:
        """Encodes and sends a message to SQS, logs success or raises error.

        Args:
            message: The message to be sent to the SQS queue.
        Raises:
            Exception: If there is an error while sending the message.
        """
        if self.session:
            async with self.session.create_client(
                "sqs",
                region_name=self.aws_region,
            ) as client:
                try:
                    message_base64 = base64.b64encode(message.message).decode("utf-8")
                    message_payload = {
                        "task_id": message.task_id,
                        "task_name": message.task_name,
                        "message": message_base64,
                        "labels": message.labels,
                    }
                    message_json = json.dumps(message_payload)
                    await client.send_message(
                        QueueUrl=self.queue_url,
                        MessageBody=message_json,
                    )
                    logger.info("Message sent")
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    raise e

    async def listen(self) -> AsyncGenerator[AckableMessage, None]:
        """Continuously polls SQS for messages, yielding and processing each one.

        Yields:
            AckableMessage: An object representing the
            received message that can be acknowledged.
        Raises:
            Exception: If there is an error while receiving messages.
        """
        if not self.session:
            return
        async with self.session.create_client(
            "sqs",
            region_name=self.aws_region,
        ) as client:
            while True:
                try:
                    response = await client.receive_message(
                        QueueUrl=self.queue_url,
                        MaxNumberOfMessages=self.max_messages,
                        WaitTimeSeconds=self.wait_time,
                        MessageAttributeNames=["All"],
                    )
                    messages = response.get("Messages", [])
                    for msg in messages:
                        logger.info("Message received")

                        message_data = json.loads(msg["Body"])
                        message_bytes = base64.b64decode(message_data["message"])
                        yield AckableMessage(
                            data=message_bytes,
                            ack=lambda receipt_handle=msg[  # type: ignore[misc]
                                "ReceiptHandle"
                            ]: self.acknowledge_message(client, receipt_handle),
                        )
                except Exception as e:
                    logger.error(f"Error receiving messages: {e}")
                    raise e

    async def acknowledge_message(
        self,
        client: AioBaseClient,
        receipt_handle: str,
    ) -> None:
        """Acknowledges and deletes a processed SQS message, logs or raises error.

        Args:
            client: The SQS client used to communicate with the AWS service.
            receipt_handle: The receipt handle of the message to acknowledge.
        Raises:
            Exception: If there is an error while acknowledging the message.
        """
        try:
            await client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle,
            )
            logger.info("Message acknowledged")
        except Exception as e:
            logger.error(f"Error acknowledging message: {e}")
            raise e
