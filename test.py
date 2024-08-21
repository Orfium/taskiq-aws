import asyncio
import uuid

from taskiq import AckableMessage, AsyncBroker, BrokerMessage

from taskiq_sqs import SQSBroker


async def main():

    sqs_broker = SQSBroker(
        queue_url="http://localhost:4510/000000000000/Queue", aws_region="us-east-1"
    )
    return await sqs_broker.kick(
        BrokerMessage(
            task_id=uuid.uuid4().hex,
            task_name=uuid.uuid4().hex,
            message=b"my_msg",
            labels={
                "label1": "val1",
            },
        )
    )


print(asyncio.run(main()))
