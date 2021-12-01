import sys
import asyncio
from message_broker import AsyncConsumer as Consumer


topic = sys.argv[1]
message_count = int(sys.argv[2])


if len(sys.argv) > 3:
    consumer_number = int(sys.argv[3])
else:
    consumer_number = 0

if len(sys.argv) > 4:
    broadcast = sys.argv[4].lower() == 'true'
else:
    broadcast = False

if consumer_number or broadcast:
    extra_config = {
        'consumer_number': consumer_number,
        'broadcast': broadcast
    }
else:
    extra_config = {}


async def main():
    counter = 0
    async with Consumer(topic, extra_config=extra_config) as consumer:
        async for message in consumer:
            print(message.value)
            print(message.key)
            counter += 1
            if counter == message_count:
                break

asyncio.run(main())
