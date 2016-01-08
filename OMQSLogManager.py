#! /usr/bin/python
# -*- coding: utf-8 -*-

# ArtCM OMQS logger manager Class
#
# (C) ArtCM 2015
#
# Initial Date: 2015.9.25

__author__ = 'dennis'

import logging
import logging.handlers
import logging.config
import ConfigReader


class OMQSLogManager(object):

    LOG_FORMAT = '%(levelname) -5s %(asctime)s %(filename) -10s:%(lineno) -5d: %(message)s'

    def __init__(self, name='OMQS', level=None, config_file='OMQS.cfg', file_name=None):
        self._name = name
        self._logger = None
        self._file_name = None
        self._level = level

        try:
            config = ConfigReader.ConfigReader()
            config.read(config_file)
            log_folder = config.Log.FOLDER
            log_level = config.Log.LEVEL
            log_format = config.Log.FORMAT
            log_type = config.Log.TYPE
            rotation = config.Log.ROTATION
            rotation_type = config.Log.ROTATION_TYPE
            max_size = int(config.Log.SIZE) * 1024 * 1024
            backup_count = config.Log.BACKUP_COUNT
            rotating_time = config.Log.ROTATING_TIME

            if not self._level:
                self._level = log_level

            if not log_format:
                log_format = OMQSLogManager.LOG_FORMAT

            if not file_name:
                file_name = 'OMQS.log'
            self._file_name = log_folder + '/' + file_name

            self._logger = logging.getLogger(self._name)

            if log_type == 'file':
                if rotation :
                    if rotation_type == 'size':
                        handler = logging.handlers.RotatingFileHandler(filename=self._file_name,
                                                                       maxBytes=max_size,
                                                                       backupCount=backup_count)
                    elif rotation_type == 'time':
                        i = rotating_time[0]
                        w = rotating_time[1]

                        if i == 'W' or i == 'w' or i == 'M' or i == 'm':
                            w = rotating_time
                            i = None

                        print w, i

                        handler = logging.handlers.TimedRotatingFileHandler(filename=self._file_name,
                                                                            when=w,
                                                                            interval=i,
                                                                            backupCount=backup_count)
                    else:
                        handler = logging.FileHandler(self._file_name)
                else:
                    handler = logging.FileHandler(self._file_name)
            else:
                handler = logging.StreamHandler()

            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(self._level)

        except Exception, e:
            logging.error('[OMQSLogger] Failed to read the config: %s', str(e))

    @property
    def logger(self):
        if self._logger:
            return self._logger
        else:
            logging.warning('[OMQSLogger] logger not initialized! Using default logger instead.')
            return logging.getLogger(__name__)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        if isinstance(value, basestring):
            self._level = value
            if self._logger:
                self._logger.setLevel(value)

    @property
    def file_name(self):
        return self._file_name

    @property
    def name(self):
        return self._name


def main():
    manager = OMQSLogManager()
    log = manager.logger
    log.info('info test')
    log.debug('debug test 1')

    manager.level = 'DEBUG'
    log.debug('debug test 2')

    manager.level = 'INFO'
    log.debug('debug test 3')

    log.setLevel('DEBUG')
    log.debug('debug test 4')


if __name__ == '__main__':
    main()

