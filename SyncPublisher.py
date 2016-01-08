#! /usr/bin/python
# -*- coding: utf-8 -*-

# ArtCM OMQS Synchronous Publisher Class
#
# (C) ArtCM 2015
#
# Initial Date: 2015.9.28

__author__ = 'dennis'

from ConfigReader import ConfigReader

import logging
import pika
import time


class OMQSSyncPublisher(object):

    # NOTE: The config values are loaded as following priorities:
    # 1. the parameters passed in
    # 2. the global config file
    # 3. the following default value
    URL = 'amqp://guest:guest@localhost:5672/%2F?'
    EXCHANGE = 'omqs.default.topicExchange'
    EXCHANGE_TYPE = 'topic'
    ROUTING_KEY = 'omqs.default.syncPublisher.key'


    def __init__(self, amqp_url=None,
                 exchange_name=None, exchange_type=None, exchange_durable=False):
        """Setup the example publisher object, passing in the URL we will use
        to connect to RabbitMQ.

        :param str amqp_url: The URL for connecting to RabbitMQ

        """
        self._connection = None
        self._channel = None
        self._message_number = 0
        self._ready = False
        self._url = amqp_url
        self._exchange_durable = exchange_durable

        # Read the global config file
        config = ConfigReader()
        config.read("OMQS.cfg")

        if not self._url:
            self._url = config.Global.MQURL
            if not self._url:
                self._url = URL

        if exchange_name:
            self._exchange = exchange_name
        else:
            self._exchange = config.SyncPublisher.EXCHANGE
            if not self._exchange:
                self._exchange = EXCHANGE

        if exchange_type:
            self._exchange_type = exchange_type
        else:
            self._exchange_type = config.SyncPublisher.EXCHANGE_TYPE
            if not self._exchange_type:
                self._exchange_type = EXCHANGE_TYPE

        self._default_key = config.SyncPublisher.ROUTING_KEYS
        if not self._default_key:
            self._default_key = ROUTING_KEYS


    def run(self):
        parameters = pika.URLParameters(self._url)
        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange,
                                       type=self._exchange_type,
                                       durable=self._exchange_durable)


    def publish_message(self, routing_key, message):
        if not routing_key:
            routing_key = self._default_key

        self._channel.basic_publish(self._exchange, routing_key, message,
                                    pika.BasicProperties(content_type='text/plain', delivery_mode=1))


    def stop(self):
        self._connection.close()



def main():

    # Connect to localhost:5672 as guest with the password guest and virtual host "/" (%2F)
    #example = OMQSSyncPublisher(amqp_url='amqp://artcm:111@192.168.0.197:5672/%2F')
    example = OMQSSyncPublisher(amqp_url='amqp://artcm:111@192.168.31.225:5672/%2F')

    try:
        example.run()
        for i in range(1, 10):
            example.publish_message('debug', 'test debug log')
            example.publish_message('info', 'test info log')
            example.publish_message('error', 'test error log')
            time.sleep(1)
    except KeyboardInterrupt:
        example.stop()

    example.stop()

if __name__ == '__main__':
    main()