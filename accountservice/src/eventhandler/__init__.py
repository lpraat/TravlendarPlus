import threading
import time

import pika

from src.configs import RABBITMQ_IP, RABBITMQ_PORT
from src.constants import ACCOUNT_EXCHANGE, ACCOUNT_QUEUE, USER, CALENDAR_QUEUE, INSTRUCTIONS_QUEUE, EVENT_QUEUE


def create_connection(ip, port):
    """
    Creates a connection to the rabbitmq server
    :param ip: the rabbitmq ip
    :param port: the rabbitmq port
    :return: a pika blocking connection
    """
    return pika.BlockingConnection(pika.ConnectionParameters(host=ip, port=port))


def setup_channel_for_sending():
    """
    Setups a new Blocking connection with the rabbitmq server
    and declares all the exchanges and queues needed for sending events.
    """
    connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
    channel = connection.channel()

    channel.exchange_declare(exchange=ACCOUNT_EXCHANGE, exchange_type='topic') # exchange topic-based
    channel.queue_declare(queue=ACCOUNT_QUEUE, durable=True)
    channel.queue_declare(queue=CALENDAR_QUEUE, durable=True)
    channel.queue_declare(queue=INSTRUCTIONS_QUEUE, durable=True)
    channel.queue_declare(queue=EVENT_QUEUE, durable=True)

    channel.confirm_delivery()  # this assures the at least once delivery of a message

    def send_heartbeats():
        """
        Sends tcp heartbeats to keep alive the connection with rabbitmq.
        """
        while True:
            time.sleep(2)
            connection.process_data_events()

    t = threading.Thread(target=send_heartbeats)
    t.daemon = True
    t.start()

    return channel


def setup_channel_for_receiving():
    """
    Setups a new Blocking connection with the rabbitmq server
    and declares all the exchanges and queues needed for sending events.
    """
    connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
    channel = connection.channel()

    channel.exchange_declare(exchange=ACCOUNT_EXCHANGE, exchange_type='topic')
    channel.queue_declare(queue=ACCOUNT_QUEUE, durable=True)
    channel.queue_bind(exchange=ACCOUNT_EXCHANGE,
                       queue=ACCOUNT_QUEUE,
                       routing_key=USER)

    return channel
