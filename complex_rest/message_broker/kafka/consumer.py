import uuid

from kafka import KafkaConsumer

from aiokafka import AIOKafkaConsumer

from .kafka_control import KafkaControl
from ..abstract_consumer import AbstractConsumer, AbstractAsyncConsumer
from ..message import Message


class BaseKafkaConsumer:
    def __init__(
            self, topic, binary=False, key_deserializer=None, value_deserializer=None,
            config=None, extra_config=None
    ):
        self.key_deserializer = key_deserializer
        self.binary = binary
        self.value_deserializer = value_deserializer

        config = config or {}
        self.extra_config = extra_config or {}

        kafka_control = KafkaControl(config)
        kafka_control.create_topic_if_not_exist(topic, self.extra_config.get('consumer_number', 1))

        config = self.process_broadcast_extra_config(config, self.extra_config)

        kafka_control.partitions_auto_increment(topic, config['group_id'])

        self.create_kafka_consumer(topic, config)

        self.process_consumer_number_extra_config(kafka_control, topic, self.extra_config)

    def create_kafka_consumer(self, topic, config):
        raise NotImplementedError

    def get_message_obj(self, kafka_message_obj):
        """
        Creates Message object based on parameters: binary, key_deserializer, value_deserializer
        :param kafka_message_obj: message object from kafka
        :return: Message object
        """
        if self.binary:
            message_value = kafka_message_obj.value
        elif self.value_deserializer:
            message_value = self.value_deserializer(kafka_message_obj.value)
        else:
            message_value = kafka_message_obj.value.decode()

        if kafka_message_obj.key is None or self.binary is True:
            message_key = kafka_message_obj.key
        elif self.key_deserializer:
            message_key = self.key_deserializer(kafka_message_obj.key)
        else:
            message_key = kafka_message_obj.key.decode()

        return Message(
            value=message_value,
            key=message_key
        )

    def process_consumer_number_extra_config(self, kafka_control, topic, extra_config):
        """
        Process consumer_number config (how many partitions for topic to create)
        """

        # if extra config has partition number more then one create partitions
        partition_number = extra_config.get('consumer_number', 1)
        if partition_number > 1:
            kafka_control.create_partitions(topic, partition_number)

    def process_broadcast_extra_config(self, kafka_config, extra_config):
        """
        Process broadcast config. For every consumer will be generated unique group_id in kafka
        :param kafka_config:
        :param extra_config:
        :return:
        """
        kafka_config = kafka_config.copy()
        # if broadcast option generate unique group id
        broadcast = extra_config.get('broadcast', False)
        if broadcast:
            group_id = uuid.uuid4().hex
            kafka_config['group_id'] = group_id
            kafka_config['auto_offset_reset'] = 'latest'
        return kafka_config


class Consumer(AbstractConsumer, BaseKafkaConsumer):
    def __init__(
            self, topic, binary=False, key_deserializer=None, value_deserializer=None, config=None, extra_config=None
    ):
        BaseKafkaConsumer.__init__(self, topic, binary, key_deserializer, value_deserializer, config, extra_config)

    def create_kafka_consumer(self, topic, config):
        self.kafka_consumer = KafkaConsumer(
            topic,
            **config,
        )

    def __iter__(self):
        return self

    def __next__(self):
        kafka_message_obj = next(self.kafka_consumer)
        return self.get_message_obj(kafka_message_obj)

    def start(self):
        pass

    def stop(self):
        self.kafka_consumer.close()


class AsyncConsumer(AbstractAsyncConsumer, BaseKafkaConsumer):
    def __init__(
            self, topic, binary=False, key_deserializer=None, value_deserializer=None, config=None, extra_config=None
    ):
        BaseKafkaConsumer.__init__(self, topic, binary, key_deserializer, value_deserializer, config, extra_config)

    def create_kafka_consumer(self, topic, config):
        self.kafka_consumer = AIOKafkaConsumer(
            topic,
            **config,
        )

    def __aiter__(self):
        return self

    async def __anext__(self):
        kafka_message_obj = await self.kafka_consumer.getone()
        return self.get_message_obj(kafka_message_obj)

    async def start(self):
        await self.kafka_consumer.start()

    async def stop(self):
        await self.kafka_consumer.stop()

        

