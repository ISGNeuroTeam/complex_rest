import importlib


class MessageBrokerBackends:
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
    }
}


def import_message_broker_module(module, backend=MessageBrokerBackends.KAFKA):
    """
    Import module for message broker backend
    :param backend: message broker name, kafka by default
    :param module: 'producer' or 'consumer'
    :return:
    producer or consumer module
    """
    assert module == 'producer' or module == 'consumer'
    module_name = f'message_broker.{backend}.{module}'
    try:
        module = importlib.import_module(module_name)
    except ImportError as err:
        raise ValueError('Wrong backend for consumer') from err
    return module


def Consumer(
        topic, binary=False, key_deserializer=None, value_deserializer=None,
        config=None, backend=MessageBrokerBackends.KAFKA
):
    """
    fabric method for consumer

    :param topic: topic to consume messages
    :param binary: if binary=True then no deserialization and Message.value and Message.key will be binary
    :param key_deserializer:  callable, key desirializer
    :param value_deserializer:  callable, value desirilizer
    :param backend: which backend to use, default is kafka
    :param config: config dictionary for connection
    :return:
    Message broker consumer instance
    """
    if config is None:
        config = MESSAGE_BROKER_DEFAULT_CONFIG[backend]['consumer']
    module = import_message_broker_module('consumer', backend)
    consumer = module.Consumer(topic, binary, key_deserializer, value_deserializer, config)
    return consumer


def AsyncConsumer(
        topic, binary=False, key_deserializer=None, value_deserializer=None,
        config=None, backend=MessageBrokerBackends.KAFKA
):
    """
    fabric method for asynchronous consumer

    :param topic: topic to consume messages
    :param binary: if binary=True then no deserialization and Message.value and Message.key will be binary
    :param key_deserializer:  callable, key desirializer
    :param value_deserializer:  callable, value desirilizer
    :param backend: which backend to use, default is kafka
    :param config: config dictionary for connection
    :return:
    Message broker consumer instance
    """
    if config is None:
        config = MESSAGE_BROKER_DEFAULT_CONFIG[backend]['consumer']
    module = import_message_broker_module('consumer', backend)
    consumer = module.AsyncConsumer(topic, binary, key_deserializer, value_deserializer, config)
    return consumer


def Producer(
        key_serializer=None, value_serializer=None,
        backend=MessageBrokerBackends.KAFKA, config=None
):
    """
    fabric method for producer


    :param key_serializer: callable, serializer for key
    :param value_serializer:  callable, serializer for value
    :param backend: which backend to use, default is kafka
    :param config: config dictionary for connection
    :return:
    Message broker producer instance
    """
    if config is None:
        config = MESSAGE_BROKER_DEFAULT_CONFIG[backend]['producer']

    module = import_message_broker_module('producer', backend)
    producer = module.Producer(key_serializer, value_serializer, config)
    return producer


def AsyncProducer(
        key_serializer=None, value_serializer=None,
        backend=MessageBrokerBackends.KAFKA, config=None
):
    """
    fabric method for asynchronous producer

    :param key_serializer: callable, serializer for key
    :param value_serializer:  callable, serializer for value
    :param backend: which backend to use, default is kafka
    :param config: config dictionary for connection
    :return:
    Message broker producer instance
    """
    if config is None:
        config = MESSAGE_BROKER_DEFAULT_CONFIG[backend]['producer']

    module = import_message_broker_module('producer', backend)
    producer = module.AsyncProducer(key_serializer, value_serializer, config)
    return producer




