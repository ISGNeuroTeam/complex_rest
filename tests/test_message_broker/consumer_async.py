import sys
import asyncio
from message_broker import AsyncConsumer as Consumer


topic = sys.argv[1]
message_count = int(sys.argv[2])



async def main():
    counter = 0
    async with Consumer(topic) as consumer:
        async for message in consumer:
            print(message.value)
            print(message.key)
            counter += 1
            if counter == message_count:
                break

asyncio.run(main())
