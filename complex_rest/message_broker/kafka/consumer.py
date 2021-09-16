from kafka import KafkaConsumer
from aiokafka import AIOKafkaConsumer
from ..abstract_consumer import  AbstractConsumer, AbstractAsyncConsumer
from ..message import Message


class Consumer(AbstractConsumer):
    def __init__(self, topic, config):
        self.kafka_consumer = KafkaConsumer(
            topic,
            **config,
        )

    def __iter__(self):
        return self

    def __next__(self):
        kafka_message_obj = next(self.kafka_consumer)
        return Message(kafka_message_obj.value.decode(), key=kafka_message_obj.key.decode())

    def start(self):
        pass

    async def stop(self):
        pass


class AsyncConsumer(AbstractAsyncConsumer):
    def __init__(self, topic, config):
        self.kafka_consumer = AIOKafkaConsumer(
            topic,
            **config,
        )

    def __aiter__(self):
        return self

    async def __anext__(self):
        kafka_message_obj = await self.kafka_consumer.getone()
        return Message(kafka_message_obj.value.decode(), key=kafka_message_obj.key.decode())

    async def start(self):
        await self.kafka_consumer.start()

    async def stop(self):
        await self.kafka_consumer.stop()
        
        

