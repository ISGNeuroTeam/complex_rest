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
            if type(message_value) == str:
                message_value = message_value.encode()
        elif isinstance(value, str):
            message_value = value.encode()
        elif type(value) in (bytes, bytearray, memoryview, type(None)):
            message_value = value
        else:
            raise ValueError('Need value serializer')

        if self.key_serializer:
            message_key = self.key_serializer(key)
            if type(message_key) == str:
                message_key = message_key.encode()
        elif type(key) in (bytes, bytearray, memoryview, type(None)):
            message_key = key
        elif isinstance(key, str):
            message_key = key.encode()
        else:
            raise ValueError('Need key serializer')

        return message_value, message_key


class Producer(AbstractProducer, BaseKafkaProducer):
    def __init__(self, key_serializer=None, value_serializer=None, kafka_producer_config=None, extra_config=None):
        """
        :param key_serializer: callable, serializer for key
        :param value_serializer:
        :param kafka_producer_config:
        :param extra_config:
        """
        BaseKafkaProducer.__init__(self, key_serializer, value_serializer)
        kafka_producer_config = kafka_producer_config or {}
        self.extra_config = extra_config or {}

        self.kafka_producer = KafkaProducer(
            **kafka_producer_config
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
    def __init__(self, key_serializer=None, value_serializer=None, config=None, extra_config=None):
        BaseKafkaProducer.__init__(self, key_serializer, value_serializer)
        config = config or {}
        self.extra_config = extra_config or {}

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



