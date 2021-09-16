from abc import ABC, abstractmethod


class AbstractProducer(ABC):
    """
    Abstract producer. Sends message through message broker. May be used as context manager
    """

    @abstractmethod
    def __init__(self, config):
        raise NotImplementedError

    @abstractmethod
    def send(self, topic, message, key=None):
        """
        Put message in message queue
        :param message: message string
        :param topic: topic, queue name, channel, etc...
        :param key: optional message key string
        :return:
        unique message id
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


class AbstractAsyncProducer(ABC):
    """
    Abstract producer. Sends message through message broker. May be used as context manager
    """

    @abstractmethod
    def __init__(self, config):
        raise NotImplementedError

    @abstractmethod
    async def send(self, topic, message, key=None):
        """
        Put message in message queue
        :param message: message string
        :param topic: topic, queue name, channel, etc...
        :param key: optional message key string
        :return:
        unique message id
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

    # @abstractmethod
    # async def message_was_consumed(self, message_id):
    #     """
    #     Checks if message was consumed
    #     :param message_id: message id
    #     :return:
    #     True if message was consumed
    #     """
    #     raise NotImplementedError
