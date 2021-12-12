from kafka import KafkaAdminClient
from kafka.admin.new_partitions import NewPartitions
from kafka.errors import InvalidPartitionsError, KafkaError
from kafka.admin.new_topic import NewTopic


class KafkaControl:
    def __init__(self, config):
        self.client = None
        self.client = KafkaAdminClient(
                bootstrap_servers=config['bootstrap_servers']
            )

    def create_partitions(self, topic, partition_number):
        try:
            rsp = self.client.create_partitions({
                topic: NewPartitions(partition_number)
            })
        # if partition number already set will be an exception
        except InvalidPartitionsError:
            pass

    def partitions_auto_increment(self, topic, consumer_group):
        topic_info = self.client.describe_topics([topic, ])[0]
        partitions_count = len(topic_info['partitions'])

        consumer_group_info = self.client.describe_consumer_groups([consumer_group, ])[0]

        # find topic consumers in consumer group
        topic_consumers = [
            member for member in consumer_group_info.members
            if member.member_assignment and len(member.member_assignment.assignment) > 0 and\
            member.member_assignment.assignment[0][0] == topic
        ]

        # how many consumers at the moment
        consumers_count = len(topic_consumers)


        # create one more partition for consumer
        if consumers_count != 0 and consumers_count >= partitions_count:
            self.create_partitions(topic, consumers_count + 1)

    def create_topic_if_not_exist(self, topic, partitions):
        rsp = self.client.describe_topics([topic, ])
        # error_code == 3 means topic doesn't exist
        if rsp[0]['error_code'] == 3:
            topic = NewTopic(
                topic, partitions, 1
            )
            try:
                self.client.create_topics([topic, ])
            except KafkaError as err:
                # if several consumers each of them creates topic
                pass

    def __del__(self):
        if self.client:
            self.client.close()
