#! /usr/bin/python

# ArtCM Offline Message Queue Service (OMQS) Worker Base Class
#
# (C) ArtCM 2015
#
# Date: 2015.9.22

__author__ = 'Dennis Wu'

from multiprocessing import Process, Queue
import os, time, logging, platform

#import signal

from OMQSLogManager import OMQSLogManager
from OMQSExceptions import *
from OMQSUtils import OMQSUtils
from ConfigReader import ConfigReader



class MsgWorker(Process):
    """
    MsgWorker:  OMQS default message handler class.

    """
    def __init__(self, q, name='BaseMsgWorker'):
        super(MsgWorker, self).__init__()

        # for performance profiling
        self._isProfiling = False
        self._queue = q
        self._ready = False

        self.name = name
        self.daemon = True

        #signal.signal(signal.SIGTERM, self.signal_handler)
        #signal.signal(signal.SIGINT, self.signal_handler)

        manager = OMQSLogManager(name=__name__, file_name=name)
        self._logger = manager.logger


    def signal_handler(self, signum, frame):
        self._logger.info('[%s][%d] signal: %d', self.name, self.pid, signum)
        if signum == signal.SIGTERM or signum == signal.SIGINT :
            self._logger.info('[%s][%d] setting stop....', self.name, self.pid)
            #self.stopping = True
            # NOTE:
            # Send a fake eof msg to make sure the worker loop can
            # break from the blocking call - queue.get()
            self._queue.put('EOF')


    def run(self):
        self._logger.info('[%s][%d]: running', self.name, self.pid)

        self.worker_will_run()
        self._ready = True

        if self._queue:
            self.msg_loop()
        else:
            raise InvalidQueueError

        self.worker_will_stop()
        self._ready = False

        self._logger.info('[%s][%d] quit!', self.name, self.pid)



    def msg_loop(self):
        while True:
            try:
                msg = self._queue.get(True)
                if msg != 'EOF':
                    self.msg_did_receive(msg)
                else:
                    break
            except Exception, e:
                self._logger.error('[%s][%d] Get error when handling msg: %s. Still continue running...', self.name, self.pid, str(e))



    def worker_will_run(self):
        """ worker_will_run:

                This is the handler before the process starts, giving the opportunity to initialize the task,
                like starting the MQ service.
        """
        pass


    def msg_did_receive(self, msg):
        """ msg_did_receive:

                Abstract handler method for subclass. Override this method to handle the real task.
                The default behavior of the baseClass is just to ignore the msg.
        """
        if __debug__:
            print 'get msg: ', msg

        #TODO here

        pass


    def worker_will_stop(self):
        """ worker_will_stop:

                Abstract handler method for subclass called before the process quits,
                giving the opportunity to finalize the task, like saving the unread msg,
                or writing the log. The default behavior is just discarding all the
                unread msg and log the queue size.
        """
        self._logger.info('[%s][%d] will quit...', self.name, self.pid)
        #TODO here

        if OMQSUtils.is_linux():
            self._logger.info('[%s][%d] Approximately %d msgs unread', self.name, self.pid, self.queue.qsize())

        else:
            pass


    @property
    def ready(self):
        '''
        Return whether process is a daemon
        '''
        return self._ready


def main():
    queue = Queue()
    worker = MsgWorker(q=queue)
    worker.start()

    for i in range(1, 10):
        s = 'test msg %d' % i
        queue.put(s)

    time.sleep(3)

    # There is two ways to stop the worker:
    # 1. send a 'EOF' msg
    # 2. terminate the process directly
    # The 1st way is the graceful way which allow the worker finalize the tasks

    #queue.put('EOF')
    #time.sleep(3)

    worker.terminate()
    worker.join()

# Just for test
if __name__ == '__main__':
    main()
