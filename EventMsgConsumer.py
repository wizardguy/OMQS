#! /usr/bin/python
# -*- coding: utf-8 -*-

# ArtCM OMQS Event Consumer Class
#
# (C) ArtCM 2015
#
# Initial Date: 2015.10.6

__author__ = 'dennis'

import logging

from OMQSLogManager import OMQSLogManager
from ConfigReader import ConfigReader

from SyncConsumer import OMQSSyncConsumer

class EventMsgConsumer(OMQSSyncConsumer):

    EVENT_EXCHANGE = 'omqs.exchange.event'
    EXCHANGE_DURABLE = True
    EVENT_KEYS = ['omqs.key.event']
    EVENT_QUEUE = 'omqs.queue.event'

    def __init__(self, amqp_url=None, keys=None, queue=None, evt_callback=None, name='EventMsgConsumer'):

        self._logger = None
        try:
            config = ConfigReader()
            config.read("OMQS.cfg")

            exchange = config.EventConsumer.EXCHANGE
            ex_durable = config.EventConsumer.EXCHANGE_DURABLE

            if not keys:
                keys = config.EventConsumer.KEYS

            if not queue:
                queue = config.EventConsumer.QUEUE

        except Exception, e:
            logging.error('[%s]: Failed to read the config or setting the logger: %r', name, e)

        if not keys:
            keys = EventMsgConsumer.EVENT_KEYS

        if not queue:
            queue = EventMsgConsumer.EVENT_QUEUE

        if not exchange:
            exchange = EventMsgConsumer.EXCHANGE

        if not ex_durable:
            ex_durable = EventMsgConsumer.EXCHANGE_DURABLE

        super(EventMsgConsumer, self).__init__(name=name,
                                               amqp_url=amqp_url,
                                               exchange_name=exchange,
                                               exchange_durable=ex_durable,
                                               routing_keys=keys,
                                               queue_name=queue,
                                               queue_durable=True,
                                               callback=evt_callback)





def main():
    try:
        #consumer = EventMsgConsumer(amqp_url='amqp://artcm:111@192.168.0.197:5672/%2F')
        #consumer = EventMsgConsumer()
        consumer = EventMsgConsumer(amqp_url='amqp://artcm:111@192.168.31.225:5672/%2F')
        consumer.callback = my_callback
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()
    except Exception, e:
        print 'get the exception: %r' % e
        if consumer.ready:
            consumer.stop()


def my_callback(channel, method, properties, body):
    #manager = OMQSLogManager(name=__name__, file_name=__name__)
    #log = manager.logger
    print " [x] my_callback: %r:%r" % (method.routing_key, body,)
    #log.debug("[x] my_callback: %r:%r", method.routing_key, body,)


if __name__ == '__main__':
    main()
