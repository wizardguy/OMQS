#! /usr/bin/python
# -*- coding:utf-8-*-

# ArtCM OMQS Manager Class
#
# (C) ArtCM 2015
#
# Initial Date: 2015.9.23

__author__ = 'Dennis Woo'

""" OMQSManager
    The manager will create a inter-process queue and
    start a child process to consume the msg in the queue.
    The caller enqueue the msg without blocking.

    (C) ArtCM 2015
"""

from multiprocessing import Process, Queue
import os
import time
import logging


from LogMsgWorker import LogMsgWorker
from EventMsgWorker import EventMsgWorker
from OMQSLogManager import OMQSLogManager


class OMQSManager(object):

    def __init__(self):
        self._log_Q = Queue()
        self._log_worker = LogMsgWorker(self._log_Q)

        self._event_Q = Queue()
        self._event_worker = EventMsgWorker(self._event_Q)

        manager = OMQSLogManager(name=__name__, file_name='OMQSManager')
        self._logger = manager.logger

    def run(self):
        self._logger.info('[OMQSManager] Starting the worker...')
        try:
            self._log_worker.start()
            self._event_worker.start()
            self.wait_worker(self._event_worker)

        except Exception, e:
            self._logger.error('[OMQSManager] Failed to start the worker: %s', str(e))

    def wait_worker(self, worker):
        time.sleep(1)


    def send_fatal(self, log):
        self.send_log(log, 'fatal')

    def send_err(self, log):
        self.send_log(log, 'error')

    def send_warning(self, log):
        self.send_log(log, 'warning')

    def send_info(self, log):
        self.send_log(log, 'info')

    def send_debug(self, log):
        self.send_log(log, 'debug')

    def send_log(self, log, key='info'):
        if self._log_worker and self._log_worker.is_alive():
            msg_str = key + ':' + log
            self._log_Q.put(msg_str)
            return True
        else:
            return False

    def send_event(self, evt, key=''):
        if self._event_worker and self._event_worker.is_alive():
            evt_str = key + ':' + evt
            self._event_Q.put(evt_str)
            return True
        else:
            return False

    def get_number_of_msg_not_sent(self):
        system = platform.system()
        # Only Linux supports qsize
        if system == 'Linux':
            n_log = self._log_Q.qsize()
            n_evt = self._event_Q.qsize()
            return n_log, n_evt
        else:
            return -1, -1


    def stop(self):
        self._logger.info('[OMQSManager] Stopping the workers ...')
        #numbers = self.get_number_of_msg_not_sent()
        #self._logger.info('%d logs, %d events still unread', numbers[0], numbers[1])
        try:
            if self._log_worker.is_alive():
                # giving the chance to finish the tasks
                self.send_log('EOF')
                self._logger.info('[OMQSManager] holding on for 3 secs ...')
                time.sleep(3)
                self._log_worker.terminate()
                self._log_worker.join()
            if self._event_worker.is_alive():
                # giving the chance to finish the tasks
                self.send_event('EOF')
                self._logger.info('[OMQSManager] holding on for 3 secs ...')
                time.sleep(3)
                self._event_worker.terminate()
                self._event_worker.join()
        except Exception, e:
            self._logger.warning('[OMQSManager] error when stopping the workers: %s', str(e))


# testing
if __name__ == '__main__':
    manager = OMQSManager()

    manager.run()

    t1 = time.time()
    for i in range(1, 100):
        msg = 'msg %d' % i
        manager.send_info(msg)
        if i % 10 == 0:
            manager.send_event(msg)

    t2 = time.time()
    dt = t2 - t1
    print 'total time: %f' % dt

    time.sleep(3)
    manager.stop()
