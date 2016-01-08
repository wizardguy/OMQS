#! /usr/bin/python

# ArtCM OMQS Event Worker Class
#
# (C) ArtCM 2015
#
# Date: 2015.9.22

__author__ = 'dennis'

from multiprocessing import Queue
import threading

import os, signal, time, logging, platform
import pika
from pika.exceptions import *

from ConfigReader import ConfigReader
from MsgWorker import MsgWorker
from AsyncPublisher import OMQSAsyncPublisher
from OMQSExceptions import *
from OMQSLogManager import OMQSLogManager


class EventMsgWorker(MsgWorker):

    EVENT_KEY = 'omqs.key.event'

    def __init__(self, q, name='EventMsgWorker'):
        super(EventMsgWorker, self).__init__(q, name)

        self._MQPublisher = None
        self._MQthread = None

        manager = OMQSLogManager(name=__name__, file_name=name)
        self._logger = manager.logger


    def worker_will_run(self):
        try:
            if self._MQPublisher:
                self._MQPublisher.stop()

            self._MQPublisher = OMQSAsyncPublisher(exchange_name='omqs.exchange.event',
                                                   queue_name='omqs.queue.event',
                                                   exchange_durable=True,
                                                   queue_durable=True,
                                                   confirm=False)
            if self._MQPublisher:
                self._MQthread = threading.Thread(target=self._MQPublisher.run, name='PublishingThread')
                self._MQthread.start()

                while not self._MQPublisher.is_ready():
                    time.sleep(0.1)

                self._logger.info('[%s][%d] ready to run!', self.name, self.pid)
            else:
                raise InvalidPublisherError

        except Exception, e:
            self._logger.error('[%s][%d] error: %s. Stopping the publisher', self.name, self.pid, str(e))
            if self._MQPublisher:
                self._MQPublisher.stop()
                self._MQPublisher = None



    def msg_did_receive(self, msg):
        #print 'msg = ', msg
        try:
            if self._MQPublisher:
                index = msg.find(':')
                key = msg[0:index]
                if key == '' or not key:
                    key = EventMsgWorker.EVENT_KEY
                body = msg[index+1:]
                self._MQPublisher.publish_message(body, key)
        except Exception, e:
            self._logger.error('[%s][%d] error when publishing: %s', self.name, self.pid, str(e))
            # backup the log message if there is anything wrong of the MQ connection
            backup_file = open('./log/backup.evt', 'a')
            backup_file.write(msg+'\n')
            backup_file.close()

            # TODO here:
            # Do particular task for special work, e.g: sending txt msg or email for login



    def worker_will_stop(self):
        if self._MQPublisher:
            print 'worker will quit!!'

            self._MQPublisher.stop()
            self._MQthread.join()
            self._MQthread = None


def main():
    q = Queue()
    worker = EventMsgWorker(q)

    worker.start()

    t1 = time.time()
    for i in range(1, 100):
        msg = 'omqs.key.event:%d' % i
        q.put(msg)
        time.sleep(0.1)
    t2 = time.time()

    dt  =t2 - t1
    print 'total time: %f' % dt

    time.sleep(3)
    worker.terminate()

    worker.join()


# Just for Test
if __name__ == '__main__':
    main()



