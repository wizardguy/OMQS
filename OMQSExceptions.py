#! /usr/bin/python

# ArtCM OMQS Error Class
#
# (C) ArtCM 2015
#
# Date: 2015.9.23

__author__ = 'Dennis Wu'


class InvalidPublisherError(Exception):
    def __repr__(self):
        return 'Fatal: the publisher is invalid! Maybe it is not created successfully.'


class InvalidQueueError(Exception):
    def __repr__(self):
        return 'Fatal: the queue is invalid! Maybe it is not created successfully.'


class InvalidChannelError(Exception):
    def __repr__(self):
        return 'Fatal: the channel is invalid! Maybe it is not created successfully.'
