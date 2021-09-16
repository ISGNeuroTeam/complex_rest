from kafka import KafkaProducer
from aiokafka import AIOKafkaProducer
from ..abstract_producer import  AbstractAsyncProducer, AbstractProducer


class Producer(AbstractProducer):
    def __init__(self, config):
        self.kafka_producer = KafkaProducer(
            **config
        )

    def send(self, topic, message, key=None):
        if key:
            key = str(key).encode()

        future_respond_obj = self.kafka_producer.send(topic, message.encode(), key)
        respond_obj = future_respond_obj.get()
        # unique id is topic + partition + offset
        return topic, respond_obj.partition, respond_obj.offset

    def start(self):
        pass

    def stop(self):
        pass


class AsyncProducer(AbstractAsyncProducer):
    def __init__(self, config):
        self.kafka_producer = AIOKafkaProducer(
            **config
        )

    async def send(self, topic, message, key=None):
        if key:
            key = str(key).encode()
        respond_obj = await self.kafka_producer.send_and_wait(topic, message.encode(), key=key)

        # unique id is topic + partition + offset
        return topic, respond_obj.partition, respond_obj.offset

    async def start(self):
        await self.kafka_producer.start()

    async def stop(self):
        await self.kafka_producer.stop()



