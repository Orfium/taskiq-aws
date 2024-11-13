# TaskIQ-AWS

taskiq-aws is a plugin for taskiq that adds a new broker based on amazonm's sqs.

# Installation

To use this project you must have installed core taskiq library:
```bash
pip install taskiq
```
This project can be installed using pip:
```bash
pip install taskiq-aws
```

# Usage

Let's see the example with the sqs broker:

```python
# broker.py
import asyncio

from taskiq_aws import SQSBroker

broker = SQSBroker(queue_url=http://localhost:4566)


@broker.task
async def best_task_ever() -> None:
    """Solve all problems in the world."""
    await asyncio.sleep(5.5)
    print("All problems are solved!")


async def main():
    task = await best_task_ever.kiq()
    print(await task.wait_result())


if __name__ == "__main__":
    asyncio.run(main())
```

Launch the workers:
`taskiq worker broker:broker`
Then run the main code:
`python3 broker.py`

Brokers parameters:
* `queue_url` - url to the sqs.
* `aws_region` - aws region of the queue.
* `task_id_generator` - custom task_id genertaor.
* `result_backend` - custom result backend.
