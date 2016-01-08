#! /usr/bin/python
# -*- coding: utf-8 -*-

# ArtCM OMQS Log Consumer Class
#
# (C) ArtCM 2015
#
# Initial Date: 2015.10.6

__author__ = 'dennis'

import logging

from OMQSLogManager import OMQSLogManager
from ConfigReader import ConfigReader

from SyncConsumer import OMQSSyncConsumer

class LogMsgConsumer(OMQSSyncConsumer):

    LOG_EXCHANGE = 'omqs.exchange.log'
    EXCHANGE_DURABLE = True
    LOG_QUEUE = 'omqs.queue.log'
    LOG_KEYS = ['omqs.key.log']

    def __init__(self, keys, amqp_url=None, queue=None, queue_durable=False, log_callback=None, name='LogMsgConsumer'):

        try:
            config = ConfigReader()
            config.read("OMQS.cfg")

            exchange = config.LogConsumer.EXCHANGE
            ex_durable = config.LogConsumer.EXCHANGE_DURABLE

            if not queue:
                queue = config.LogConsumer.QUEUE

        except Exception, e:
            logging.error('[%s]: Failed to read the config or setting the logger: %r', name, e)
            return None

        if not exchange:
            exchange = LogMsgConsumer.LOG_EXCHANGE

        if not ex_durable:
            ex_durable = LogMsgConsumer.EXCHANGE_DURABLE

        if not queue:
            queue = LogMsgConsumer.LOG_QUEUE

        if not keys:
            keys = LogMsgConsumer.LOG_KEYS

        super(LogMsgConsumer, self).__init__(name=name,
                                             amqp_url=amqp_url,
                                             exchange_name=exchange,
                                             exchange_durable=ex_durable,
                                             routing_keys=keys,
                                             queue_name=queue,
                                             queue_durable=queue_durable,
                                             callback=log_callback)



def main():
    """
    :return:
    """

    """ This is an example of creating a consumer for normal log message. The queue_durable is set to False.
        Noted that the keys can be any patten following the AMQP format like: '#', '*.debug', 'kernel.*', ...
    """
    try:
        #consumer = LogMsgConsumer(amqp_url='amqp://artcm:111@192.168.0.197:5672/%2F')
        info_consumer = LogMsgConsumer(keys=['debug'], log_callback=my_callback)
        #info_consumer = LogMsgConsumer(amqp_url='amqp://artcm:111@192.168.31.225:5672/%2F',
        #                               keys=['debug', 'info'],
        #                               queue='omqs.queue.log',
        #                               queue_durable=False)
        info_consumer.callback = my_callback

        """ Another way to set the callback is passing the callback func when initializing
        """
        # info_consumer = LogMsgConsumer(amqp_url='amqp://artcm:111@192.168.31.225:5672/%2F',
        #                                keys=['debug', 'info'],
        #                                queue='omqs.queue.log',
        #                                queue_durable=False,
        #                                log_callback=my_callback)

        info_consumer.run()
    except KeyboardInterrupt:
        info_consumer.stop()
    except Exception, e:
        print 'get the exception: %r' % e
        if info_consumer.ready:
            info_consumer.stop()

    """ This is another example of creating a consumer for critical message, like error log.
        In this case, the queue_durable is set to True to make sure the message can be received.
    """

    # try:
    #     error_consumer = LogMsgConsumer(amqp_url='amqp://artcm:111@192.168.31.225:5672/%2F',
    #                                    keys=['error', 'fatal'],
    #                                    queue='omqs.queue.error',
    #                                    queue_durable=True)
    #     error_consumer.callback = my_callback
    #     error_consumer.run()
    # except KeyboardInterrupt:
    #     error_consumer.stop()
    # except Exception, e:
    #     print 'get the exception: %r' % e
    #     if error_consumer.ready:
    #         error_consumer.stop()



def my_callback(channel, method, properties, body):
    manager = OMQSLogManager(name=__name__, file_name=__name__)
    log = manager.logger
    print " [x] my_callback: %r:%r" % (method.routing_key, body,)
    #log.debug("[x] my_callback: %r:%r", method.routing_key, body,)


if __name__ == '__main__':
    main()
