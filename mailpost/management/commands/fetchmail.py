"""
A package that maps incoming email to HTTP requests
Mailpost version 0.1
(C) 2010 oDesk www.oDesk.com
"""


import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.mail import mail_admins

from mailpost.handler import Handler


class Command(BaseCommand):

    def handle(self, *args, **options):
        if settings.DISABLE_FETCHMAIL:
            print "Fetchmail is disabled"
            return False
        if os.path.exists(settings.LOCK_FILENAME):
            print "Lock file found! Cannot run another process."
            print "If you believe this is a mistake," + \
                  " please delete '%s' file manually" % \
                  os.path.normpath(settings.LOCK_FILENAME)
            mail_admins('MAILPOST:Lock file found! Cannot run another process',\
                        "If you believe this is a mistake," + \
                        " please delete '%s' file manually" % \
                        os.path.normpath(settings.LOCK_FILENAME),
                        fail_silently=True)
            return False

        handler = Handler(config_file=settings.MAILPOST_CONFIG_FILE)

        f = open(settings.LOCK_FILENAME, 'w')
        f.close()
        try:
            for url, result in handler.process():
                print 'Sent to URL: %s' % url
                if isinstance(result, Exception):
                    print 'Error: ', result
                else:
                    print 'OK'
        finally:
            os.remove(settings.LOCK_FILENAME)
