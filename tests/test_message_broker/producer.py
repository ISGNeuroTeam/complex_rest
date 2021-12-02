import sys

from message_broker import Producer

topic = sys.argv[1]
message = sys.argv[2]
key = sys.argv[3] if len(sys.argv) > 3 else None

with Producer() as producer:
    message_id = producer.send(topic, message, key=key)
    print(message_id)
