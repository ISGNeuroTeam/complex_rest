from kafka import KafkaProducer
from aiokafka import AIOKafkaProducer
from ..abstract_producer import  AbstractAsyncProducer, AbstractProducer


class BaseKafkaProducer:
    def __init__(self, key_serializer=None, value_serializer=None):
        self.key_serializer = key_serializer
        self.value_serializer = value_serializer

    def get_kafka_message(self, value, key=None):
        if self.value_serializer:
            message_value = self.value_serializer(value)
        elif isinstance(value, str):
            message_value = value.encode()
        elif type(value) in (bytes, bytearray, memoryview, type(None)):
            message_value = value
        else:
            raise ValueError('Need value serializer')

        if self.key_serializer:
            message_key = self.key_serializer(key)
        elif type(key) in (bytes, bytearray, memoryview, type(None)):
            message_key = key
        elif isinstance(key, str):
            message_key = key.encode()
        else:
            raise ValueError('Need key serializer')

        return message_value, message_key


class Producer(AbstractProducer, BaseKafkaProducer):
    def __init__(self, key_serializer=None, value_serializer=None, config=None):
        BaseKafkaProducer.__init__(self, key_serializer, value_serializer)
        config = config or {}
        self.kafka_producer = KafkaProducer(
            **config
        )

    def send(self, topic, message, key=None):
        message_value, message_key = self.get_kafka_message(message, key)
        future_respond_obj = self.kafka_producer.send(topic, message_value, message_key)
        respond_obj = future_respond_obj.get()
        # unique id is topic + partition + offset
        return topic, respond_obj.partition, respond_obj.offset

    def start(self):
        pass

    def stop(self):
        pass


class AsyncProducer(AbstractAsyncProducer, BaseKafkaProducer):
    def __init__(self, key_serializer=None, value_serializer=None, config=None):
        BaseKafkaProducer.__init__(self, key_serializer, value_serializer)
        config = config or {}
        self.kafka_producer = AIOKafkaProducer(
            **config
        )

    async def send(self, topic, message, key=None):
        message_value, message_key = self.get_kafka_message(message, key)
        respond_obj = await self.kafka_producer.send_and_wait(topic, message_value, message_key)

        # unique id is topic + partition + offset
        return topic, respond_obj.partition, respond_obj.offset

    async def start(self):
        await self.kafka_producer.start()

    async def stop(self):
        await self.kafka_producer.stop()



