import os

from kafka.consumer import KafkaConsumer
from kafka.producer import KafkaProducer
import json


class Kafka:
    def get_kafka_server(self):
        """

        :return:
        """
        # return [os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT")]
        return [os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT")]

    def kafka_consumer(self, topic, group_id):
        """

        :param topic:
        :param group_id:
        :return:
        """
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.get_kafka_server(),
            # max_poll_interval_ms=10000,
            # bootstrap_servers=[os.getenv("KAFKA_IP") + ":" + os.getenv("KAFKA_PORT")],
            auto_offset_reset="latest",
            # consumer_timeout_ms=10000,
            # enable_auto_commit=False
            # value_deserializer=lambda m: json.loads(m.decode('ascii'))
        )
        print(consumer)
        return consumer

    def kafka_producer(self, topic, values):
        """

        :param group_id:
        :param topic:
        :param values:
        :return:
        """
        producer = KafkaProducer(
            bootstrap_servers=self.get_kafka_server(),
            value_serializer=lambda m: json.dumps(m).encode("ascii"),
        )
        producer.send(topic, value=values)
