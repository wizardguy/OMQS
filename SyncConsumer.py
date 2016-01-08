#! /usr/bin/python
# -*- coding: utf-8 -*-

# ArtCM OMQS Synchronous Consumer Class
#
# (C) ArtCM 2015
#
# Initial Date: 2015.10.6


__author__ = 'dennis'

from ConfigReader import ConfigReader

from OMQSLogManager import OMQSLogManager

import pika
import logging

class OMQSSyncConsumer(object):

    # NOTE: The config values are loaded as following priorities:
    # 1. the parameters passed in
    # 2. the global config file
    # 3. the following default value
    URL = 'amqp://guest:guest@localhost:5672/%2F?'
    EXCHANGE = 'omqs.default.topicExchange'
    EXCHANGE_TYPE = 'topic'
    QUEUE = 'omqs.default.topicQueue'
    KEYS = ['omqs.default.syncPublisher.key']


    def __init__(self,
                 name='BaseSyncConsumer',
                 amqp_url=None,
                 exchange_name=None,
                 exchange_type=None,
                 exchange_durable=False,
                 queue_name=None,
                 queue_durable=False,
                 routing_keys=None,
                 no_ack=True,
                 callback=None):
        """Setup the example publisher object, passing in the URL we will use
        to connect to RabbitMQ.

        :param str amqp_url: The URL for connecting to RabbitMQ

        """
        self._name = name
        self._connection = None
        self._channel = None
        self._message_number = 0
        self._exchange_durable = exchange_durable
        self._queue_durable = queue_durable
        self._no_ack = no_ack
        self._callback = callback

        manager = OMQSLogManager(name=name, file_name=name)
        self._logger = manager.logger

        # Read the global config file
        config = ConfigReader()
        config.read("OMQS.cfg")

        if amqp_url:
            self._url = amqp_url
        else:
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

        if queue_name:
            self._queue = queue_name
        else:
            self._queue = config.SyncPublisher.QUEUE
            if not self._queue:
                self._queue = QUEUE

        if routing_keys:
            self._routing_keys = routing_keys
        else:
            self._keys = []
            str_keys = config.SyncPublisher.ROUTING_KEYS
            if str_keys:
                keys = str_keys.split(',')
                for key in keys:
                    self._routing_keys.append(key.strip())
            else:
                self._routing_keys = KEYS

        if not self._callback:
            self._callback = default_callback


    def run(self):
        self._logger.info('[%s] Establishing connection to %s...', self._name, self._url)
        parameters = pika.URLParameters(self._url)
        self._connection = pika.BlockingConnection(parameters)

        self._logger.info('[%s] Setting up exchange(%s) and queue(%s)', self._name, self._exchange, self._queue)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(exchange=self._exchange,
                                       type=self._exchange_type,
                                       durable=self._exchange_durable)

        #result = channel.queue_declare(exclusive=True)
        #queue_name = result.method.queue

        self._channel.queue_declare(queue=self._queue,
                                    durable=self._queue_durable,
                                    auto_delete=False)

        self._logger.info('[%s] Binding keys %r ...', self._name, self._routing_keys)
        for binding_key in self._routing_keys:
            self._channel.queue_bind(exchange=self._exchange,
                                     queue=self._queue,
                                     routing_key=binding_key)

        self._channel.basic_consume(consumer_callback=self._callback,
                                    queue=self._queue,
                                    no_ack=self._no_ack)

        self._logger.info('[%s] Starting consuming messages ...', self._name)
        self._channel.start_consuming()



    def stop(self):
        self._connection.close()
        self._logger.info('[%s] connection closed!', self._name)


    @property
    def callback(self):
        return self._callback


    @callback.setter
    def callback(self, value):
        self._callback = value
        if not self._callback:
            self._callback = default_callback

    @property
    def ready(self):
        if self._connection and self._channel:
            return self._connection.is_open and self._channel.is_open
        else:
            return False

    @property
    def keys(self):
        return self._keys

    @property
    def exchange(self):
        return self._exchange

    @property
    def exchange_type(self):
        return self._exchange_type

    @property
    def queue(self):
        return self._queue

    @property
    def queue_durable(self):
        return self._queue_durable



def default_callback(channel, method, properties, body):
    """ Abstract msg handler. The subclass should override this callback.
    The default behavior of the callback is just print the message body and increase the message number.

        :param channel: the channel of current connection
        :param method: the method of current channel. You can get the routing key by method.routing_key
        :param properties: the properties of current channel
        :param body: msg body
        :return: None
        """
    print " [x] %r:%r" % (method.routing_key, body,)




def main():

    # Connect to localhost:5672 as guest with the password guest and virtual host "/" (%2F)
    #example = OMQSSyncConsumer(amqp_url='amqp://artcm:111@192.168.0.197:5672/%2F')
    example = OMQSSyncConsumer(amqp_url='amqp://artcm:111@192.168.31.225:5672/%2F', routing_keys=['debug', 'info', 'error'])

    try:
        example.run()
    except KeyboardInterrupt:
        example.stop()

if __name__ == '__main__':
    main()

