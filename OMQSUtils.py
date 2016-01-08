# OMQSUtils.py
#
# (C) ArtCM 2015
#
# Date: 2015.9.22


__author__ = 'dennis'

import platform, os

class OMQSUtils(object):

    @staticmethod
    def is_linux():
        system = platform.system()
        if system == 'Linux':
            return True
        else:
            return False

