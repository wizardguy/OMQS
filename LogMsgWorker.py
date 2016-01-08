#! /usr/bin/python

# ArtCM OMQS Log Worker Class
#
# (C) ArtCM 2015
#
# Date: 2015.9.22


__author__ = 'dennis'

from multiprocessing import Queue

import time, logging, os, sys

from ConfigReader import ConfigReader
from MsgWorker import MsgWorker
from SyncPublisher import OMQSSyncPublisher
from OMQSExceptions import *
from OMQSLogManager import OMQSLogManager


class LogMsgWorker(MsgWorker):
    def __init__(self, q, name='LogMsgWorker'):
        super(LogMsgWorker, self).__init__(q, name)

        self._MQPublisher = None
        self._logger = None

        manager = OMQSLogManager(name=__name__, file_name=name)
        self._logger = manager.logger


    def worker_will_run(self):
        try:
            if self._MQPublisher:
                self._MQPublisher.stop()

            self._MQPublisher = OMQSSyncPublisher(exchange_name='omqs.exchange.log',
                                                  exchange_type='topic',
                                                  exchange_durable=True)
            if self._MQPublisher:
                self._MQPublisher.run()
            else:
                raise InvalidPublisherError

        except Exception, e:
            self._logger.error('[%s][%d] Failed to start the publisher: %s', self.name, self.pid, str(e))
            if self._MQPublisher:
                self._MQPublisher.stop()
                self._MQPublisher = None


    def msg_did_receive(self, msg):
        if self._MQPublisher:
            try:
                # Each log msg would be as following format: '[type]:[body]'
                # for example:
                # fatal: fatal msg
                # error: error msg
                # warning: warning msg
                # info: info msg
                # debug: debug msg
                #
                #strs = msg.split(':')

                index = msg.find(':')
                key = msg[0:index]
                body = msg[index+1:]
                self._MQPublisher.publish_message(key, body)
            except Exception, e:
                self._logger.error('[%s][%d] Failed to publish the publisher: %s', self.name, self.pid, str(e))
                # backup the log message if there is anything wrong of the MQ connection
                backup_file = open('./log/backup.log', 'a')
                backup_file.write(msg+'\n')
                backup_file.close()


    def worker_will_stop(self):
        if self._MQPublisher:
            try:
                self._MQPublisher.stop()
            except Exception, e:
                self._MQPublisher = None
                self._logger.warning('[%s][%d] Error when stopping publisher: %s', self.name, self.pid, str(e))




def main():

    q = Queue()
    worker = LogMsgWorker(q)

    worker.start()
    t1 = time.time()
    for i in range(1, 100):
        q.put('info:this is test log %d' % i)
        q.put('debug:this is test log %d' % i)
        q.put('error:this is test error log %d' % i)
        q.put('fatal:this is test fatal log %d' % i)
        time.sleep(0.1)
    t2 = time.time()
    dt = t2 - t1
    print 'total time: %f' % dt

    time.sleep(3)

    worker.terminate()
    worker.join()


# Just for Test
if __name__ == '__main__':
    main()



