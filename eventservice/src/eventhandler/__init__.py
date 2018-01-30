import threading
import time

import pika

from src.configs import RABBITMQ_IP, RABBITMQ_PORT
from src.constants import CALENDAR_EXCHANGE, \
    EVENT_EXCHANGE, EVENT_QUEUE, CALENDAR_CREATED, CALENDAR_DELETED, EVENT, INSTRUCTIONS_QUEUE, PREFERENCES_DELETED


def create_connection(ip, port):
    """
    Creates a connection to the rabbitmq server
    :param ip: the rabbitmq ip
    :param port: the rabbitmq port
    :return: a pika blocking connection
    """
    return pika.BlockingConnection(pika.ConnectionParameters(host=ip, port=port))


def setup_channel_for_sending(app_ctx=True):
    """
    Setups a new Blocking connection with the rabbitmq server
    and declares all the exchanges and queues needed for sending events.
    :param app_ctx: true if this method is called in a flask app context false otherwise
    """
    connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
    channel = connection.channel()

    channel.exchange_declare(exchange=EVENT_EXCHANGE, exchange_type='topic')
    channel.queue_declare(queue=EVENT_QUEUE, durable=True)
    channel.queue_declare(queue=INSTRUCTIONS_QUEUE, durable=True)

    channel.confirm_delivery() # this assures the at least once delivery of a message

    if app_ctx:
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

    channel.exchange_declare(exchange=CALENDAR_EXCHANGE, exchange_type='topic')

    channel.exchange_declare(exchange=EVENT_EXCHANGE, exchange_type='topic')

    channel.queue_declare(queue=EVENT_QUEUE, durable=True)

    for routing_key in (CALENDAR_CREATED, CALENDAR_DELETED, PREFERENCES_DELETED):
        channel.queue_bind(exchange=CALENDAR_EXCHANGE,
                           queue=EVENT_QUEUE,
                           routing_key=routing_key)

    channel.queue_bind(exchange=EVENT_EXCHANGE,
                       queue=EVENT_QUEUE,
                       routing_key=EVENT)

    return channel
