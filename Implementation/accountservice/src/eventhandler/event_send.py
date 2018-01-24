import logging

import pika

from src.constants import ACCOUNT_EXCHANGE

logger = logging.getLogger(__name__)


def publish_event(channel, event, routing_key):
    """
    Sends the message to the message broker through channel.
    :param channel: the channel.
    :param event: the event to be sent.
    :param routing_key: the routing key for the topic-matching.
    :return: true if the event could be routed false otherwise
    """
    logging.info(f"Publishing event {event.__dict__}")
    return channel.basic_publish(exchange=ACCOUNT_EXCHANGE,
                                 routing_key=routing_key,
                                 mandatory=True,  # thanks to this the basic publish returns false if tehre are no
                                                  # queue to route the message to
                                 properties=pika.BasicProperties(delivery_mode=2),
                                 body=event.toJSON())