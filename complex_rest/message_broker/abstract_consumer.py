from abc import ABC, abstractmethod


class AbstractConsumer(ABC):
    """
    Abstract consumer. Iterator through messages. May be used as context manager
    """

    @abstractmethod
    def __init__(self, topic, binary=False, key_deserializer=None, value_deserializer=None, config=None):
        """
        :param topic: topic to consume messages
        :param binary: if binary=True then no deserialization and Message.value and Message.key will be binary
        :param key_deserializer:  callable, key desirializer
        :param value_deserializer:  callable, value desirilizer
        :param config: configuration dictionary for message broker adapter
        """
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self):
        """
        :return:
        next Message object
        """
        raise NotImplementedError

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()


class AbstractAsyncConsumer(ABC):
    """
    Abstract consumer. Asynchronous iterator through messages. May be used as context manager
    """
    @abstractmethod
    def __init__(self, topic, binary=False, key_deserializer=None, value_deserializer=None, config=None):
        """
        :param topic: topic to consume messages
        :param binary: if binary=True then no deserialization and Message.value and Message.key will be binary
        :param key_deserializer:  callable, key desirializer
        :param value_deserializer:  callable, value desirilizer
        :param config: configuration dictionary for message broker adapter
        """
        raise NotImplementedError

    @abstractmethod
    def __aiter__(self):
        return self

    @abstractmethod
    async def __anext__(self):
        """
        :return:
        next Message object
        """
        raise NotImplementedError

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        await self.stop()

