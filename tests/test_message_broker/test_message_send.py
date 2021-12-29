import os
import subprocess
import sys
import time
import asyncio
import json


from pathlib import Path
from unittest import TestCase
from kafka.admin.client import KafkaAdminClient
from message_broker import Producer, AsyncProducer, Consumer, AsyncConsumer
from core.settings import ini_config



cur_dir = Path(__file__).parent.resolve()

base_rest_dir = str(cur_dir.parent.parent / 'complex_rest')

producer_script = str(cur_dir / 'producer.py')
consumer_script = str(cur_dir / 'consumer.py')

producer_async_script = str(cur_dir / 'producer_async.py')
consumer_async_script = str(cur_dir / 'consumer_async.py')

def get_subprocess_env():
    subproc_env = os.environ.copy()
    subproc_env["PYTHONPATH"] = base_rest_dir
    return subproc_env

def delete_topics(topics):
    bootstrap_server = ini_config['message_broker_consumer']['bootstrap_servers']
    client = KafkaAdminClient(
        bootstrap_servers=bootstrap_server
    )
    try:
        client.delete_topics(topics)
    except Exception as err:
        pass
    try:
        client.delete_consumer_groups(['complex_rest'])
    except Exception as err:
        pass
    client.close()
    time.sleep(2)


class TestMessageSend(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        delete_topics(['test_topic', ])

    @classmethod
    def tearDownClass(cls) -> None:
        delete_topics(['test_topic', ])

    def setUp(self) -> None:
        self.consumer_proc = subprocess.Popen(
            [sys.executable, consumer_script, 'test_topic', str(1)],
            env=get_subprocess_env(),
            stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1
        )
        time.sleep(2)

    def test_producer_send(self):
        producer = Producer()
        producer.send('test_topic', 'test_message', 'test_key')
        time.sleep(2)
        message, key = self.consumer_proc.stdout.read().splitlines()

        self.assertEqual(message, 'test_message')
        self.assertEqual(key, 'test_key')

    def test_producer_async_send(self):
        async def test_main():
            async with AsyncProducer() as producer:
                await producer.send('test_topic', 'test_message_async', 'test_key_async')
        asyncio.run(test_main())
        time.sleep(2)
        message, key = self.consumer_proc.stdout.read().splitlines()

        self.assertEqual(message, 'test_message_async')
        self.assertEqual(key, 'test_key_async')

    def test_producer_serializer(self):
        producer = Producer(
            value_serializer=json.dumps
        )
        obj = {
            'integer': 1,
            'float': 2.0,
            'list': [1, 2, 3]
        }
        producer.send('test_topic', obj, 'test_key')
        time.sleep(2)
        message, key = self.consumer_proc.stdout.read().splitlines()

        self.assertDictEqual(
            obj, json.loads(message)
        )

    def test_producer_key_serializer(self):
        producer = Producer(
            key_serializer=json.dumps
        )
        test_key = {
            'test_key': 1
        }
        producer.send('test_topic', 'test_message', test_key)
        time.sleep(2)
        message, key = self.consumer_proc.stdout.read().splitlines()

        self.assertDictEqual(
            test_key, json.loads(key)
        )

    def tearDown(self) -> None:
        self.consumer_proc.kill()


class TestMessageConsume(TestCase):
    @classmethod
    def setUpClass(cls):
        delete_topics(['test_topic', 'test_topic_4part', 'test_topic_broadcast'])

    @classmethod
    def tearDownClass(cls) -> None:
        delete_topics(['test_topic', 'test_topic_4part', 'test_topic_broadcast'])

    def test_consume_message_before_consumer_start(self):
        with Producer() as producer:
            producer.send('test_topic', 'unprocessed_message')

        with Consumer('test_topic') as consumer:
            message = next(consumer)
            self.assertEqual(str(message.value), 'unprocessed_message')

    def test_do_not_consume_twice(self):
        with Producer() as producer:
            producer.send('test_topic', 'unprocessed_message')

        with Consumer('test_topic') as consumer:
            message = next(consumer)
            self.assertEqual(str(message.value), 'unprocessed_message')

        consumer_proc = subprocess.Popen(
            [sys.executable, consumer_script, 'test_topic', str(1)],
            env=get_subprocess_env(),
            stderr=subprocess.PIPE,  stdout=subprocess.PIPE, universal_newlines=True, bufsize=1
        )
        time.sleep(5)
        consumer_proc.kill()
        messages = consumer_proc.stdout.read()
        self.assertEqual(messages, '')

    def test_value_deserializer(self):
        test_dict = {'test': 1, 'test1': 'test'}
        with Producer() as producer:
            producer.send('test_topic', json.dumps(test_dict))

        with Consumer('test_topic', value_deserializer=json.loads) as consumer:
            message = next(consumer)
            self.assertDictEqual(message.value, test_dict)

    def test_key_deserializer(self):
        test_key = {'test': 1, 'test1': 'test'}
        with Producer() as producer:
            producer.send('test_topic', 'unprocessed_message', json.dumps(test_key))

        with Consumer('test_topic', key_deserializer=json.loads) as consumer:
            message = next(consumer)
            self.assertDictEqual(message.key, test_key)

    def test_several_consumers_roundrobin(self):
        self._several_consumers_roundrobin(consumer_script)

    def test_several_consumers_roundrobin_async(self):
        self._several_consumers_roundrobin(consumer_async_script)

    def _several_consumers_roundrobin(self, script):
        consumers_procs = list()
        message_count = 8
        consumer_count = 4
        # create four consumers must be created 4 partitions in topic
        for i in range(consumer_count):
            consumer_proc = subprocess.Popen(
                [sys.executable, script, 'test_topic_4part', str(2), str(consumer_count), 'false'],
                env=get_subprocess_env(),
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, bufsize=1
            )
            consumers_procs.append(consumer_proc)

        # producer sends 8 messages
        with Producer() as producer:
            for i in range(message_count):
                producer.send('test_topic_4part', f'message{i}')

        time.sleep(15)
        result_message_set = set()
        for consumer_proc in consumers_procs:
            consumer_proc.kill()

            consumer_output = consumer_proc.stdout.readlines()

            # each consumer must consume two messages
            self.assertEqual(len(consumer_output), 4)

            messages = filter(lambda x: x != 'None', [m.strip('\n') for m in consumer_output])
            result_message_set.update(messages)

        self.assertSetEqual(result_message_set, set(f'message{i}' for i in range(message_count)))

    def test_broadcast(self):
        consumers_procs = list()
        topic_name = 'test_topic_broadcast'
        consumer_count = 4
        # create four consumers must be created 4 partitions in topic
        for i in range(consumer_count):
            consumer_proc = subprocess.Popen(
                [sys.executable, consumer_script, topic_name, str(1), str(consumer_count), 'true'],
                env=get_subprocess_env(),
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True,
                bufsize=1
            )
            consumers_procs.append(consumer_proc)

        time.sleep(5)
        # producer sends 1 message and all consumers must get it
        with Producer() as producer:
            producer.send(topic_name, f'broadcast_message', 'test_key')

        time.sleep(5)

        for consumer_proc in consumers_procs:
            consumer_proc.kill()

            consumer_output = consumer_proc.stdout.readlines()
            # each consumer must consume one message
            self.assertEqual(len(consumer_output), 2)

            message = consumer_output[0].strip('\n')
            self.assertEqual(message, 'broadcast_message')


class TestMessageAsyncConsume(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        delete_topics(['test_topic', ])

    @classmethod
    def tearDownClass(cls) -> None:
        delete_topics(['test_topic', ])

    def test_consume_message_before_consumer_start(self):
        with Producer() as producer:
            producer.send('test_topic', 'unprocessed_message')

        async def consume_message():
            async with AsyncConsumer('test_topic') as consumer:
                message = await consumer.__anext__()
                self.assertEqual(str(message.value), 'unprocessed_message')
        asyncio.run(consume_message())

    def test_value_deserializer(self):
        test_dict = {'test': 1, 'test1': 'test'}
        with Producer() as producer:
            producer.send('test_topic', json.dumps(test_dict))

        async def consume():
            async with AsyncConsumer('test_topic', value_deserializer=json.loads) as consumer:
                message = await consumer.__anext__()
                self.assertDictEqual(message.value, test_dict)
        asyncio.run(consume())

    def test_key_deserializer(self):
        test_key = {'test': 1, 'test1': 'test'}
        with Producer() as producer:
            producer.send('test_topic', 'unprocessed_message', json.dumps(test_key))

        async def consume():
            async with AsyncConsumer('test_topic', key_deserializer=json.loads) as consumer:
                message = await consumer.__anext__()
                self.assertDictEqual(message.key, test_key)
        asyncio.run(consume())
