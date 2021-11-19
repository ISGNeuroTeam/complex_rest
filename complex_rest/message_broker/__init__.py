import enum
import importlib

from core.settings.ini_config import ini_config, merge_ini_config_with_defaults

from .message import Message


class MessageBrokerBackends(enum.Enum):
    KAFKA = 'kafka'
    
    
MESSAGE_BROKER_DEFAULT_CONFIG = {
    MessageBrokerBackends.KAFKA: {
        'producer': {
            'bootstrap_servers': 'localhost:9092',
            'acks': 'all',
        },
        'consumer': {
            'bootstrap_servers': 'localhost:9092',
        }
    },
}

MESSAGE_BROKER_BACKEND = MessageBrokerBackends(ini_config['message_broker']['backend'])


PRODUCER_CONFIG = merge_ini_config_with_defaults(
    ini_config['message_broker_producer'],
    MESSAGE_BROKER_DEFAULT_CONFIG[MESSAGE_BROKER_BACKEND]['producer'],
)


CONSUMER_CONFIG = merge_ini_config_with_defaults(
    ini_config['message_broker_consumer'],
    MESSAGE_BROKER_DEFAULT_CONFIG[MESSAGE_BROKER_BACKEND]['consumer'],
)


def import_message_broker_module(module):
    """
    Import module for message broker backend
    :param backend: message broker name, kafka by default
    :param module: 'producer' or 'consumer'
    :return:
    producer or consumer module
    """
    assert module == 'producer' or module == 'consumer'
    module_name = f'message_broker.{MESSAGE_BROKER_BACKEND.value}.{module}'
    try:
        module = importlib.import_module(module_name)
    except ImportError as err:
        raise ValueError('Wrong backend for consumer') from err
    return module


def Consumer(
        topic, binary=False, key_deserializer=None, value_deserializer=None,
):
    """
    fabric method for consumer

    :param topic: topic to consume messages
    :param binary: if binary=True then no deserialization and Message.value and Message.key will be binary
    :param key_deserializer:  callable, key deserializer
    :param value_deserializer:  callable, value deserializer
    :return:
    Message broker consumer instance
    """

    module = import_message_broker_module('consumer')
    consumer = module.Consumer(topic, binary, key_deserializer, value_deserializer, CONSUMER_CONFIG)
    return consumer


def AsyncConsumer(
        topic, binary=False, key_deserializer=None, value_deserializer=None,
):
    """
    fabric method for asynchronous consumer

    :param topic: topic to consume messages
    :param binary: if binary=True then no deserialization and Message.value and Message.key will be binary
    :param key_deserializer:  callable, key desirializer
    :param value_deserializer:  callable, value desirilizer
    :return:
    Message broker consumer instance
    """
    module = import_message_broker_module('consumer')
    consumer = module.AsyncConsumer(topic, binary, key_deserializer, value_deserializer, CONSUMER_CONFIG)
    return consumer


def Producer(
        key_serializer=None, value_serializer=None,
):
    """
    fabric method for producer


    :param key_serializer: callable, serializer for key
    :param value_serializer:  callable, serializer for value
    :return:
    Message broker producer instance
    """
    module = import_message_broker_module('producer')
    producer = module.Producer(key_serializer, value_serializer, PRODUCER_CONFIG)
    return producer


def AsyncProducer(
        key_serializer=None, value_serializer=None,
):
    """
    fabric method for asynchronous producer

    :param key_serializer: callable, serializer for key
    :param value_serializer:  callable, serializer for value
    :return:
    Message broker producer instance
    """
    module = import_message_broker_module('producer')
    producer = module.AsyncProducer(key_serializer, value_serializer, PRODUCER_CONFIG)
    return producer
