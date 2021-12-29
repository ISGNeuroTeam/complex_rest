#!/bin/bash

# Start zookeeper
/kafka/kafka_2.13-3.0.0/bin/zookeeper-server-start.sh /kafka/kafka_2.13-3.0.0/config/zookeeper.properties &

# Start kafka
/kafka/kafka_2.13-3.0.0/bin/kafka-server-start.sh /kafka/kafka_2.13-3.0.0/config/server.properties &
# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?

