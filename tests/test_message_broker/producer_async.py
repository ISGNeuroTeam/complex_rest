import asyncio
import sys
from message_broker import AsyncProducer as Producer

topic = sys.argv[1]
message = sys.argv[2]
try:
    key = sys.argv[3]
except IndexError:
    key = None


async def send():
    async with Producer() as producer:
        if key is not None:
            message_id = await producer.send(topic, message, key)
        else:
            message_id = await producer.send(topic, message)
        print(message_id)

asyncio.run(send())
