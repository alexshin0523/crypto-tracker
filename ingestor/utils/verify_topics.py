import json
from confluent_kafka.admin import AdminClient

#prints out list of topics to console
admin = AdminClient({'bootstrap.servers':'kafka:9092'})
topics = admin.list_topics(timeout=5).topics
print(json.dumps(list(topics.keys()), indent=2))
