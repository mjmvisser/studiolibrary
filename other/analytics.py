#Embedded file name: /automount/sun-01/home/mvisser/workspace/studiolibrary/other/analytics.py
"""
Released subject to the BSD License
Please visit http://www.voidspace.org.uk/python/license.shtml

Contact: kurt.rathjen@gmail.com
Comments, suggestions and bug reports are welcome.
Copyright (c) 2015, Kurt Rathjen, All rights reserved.

It is a very non-restrictive license but it comes with the usual disclaimer.
This is free software: test it, break it, just don't blame me if it eats your
data! Of course if it does, let me know and I'll fix the problem so that it
doesn't happen to anyone else.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
   # * Redistributions of source code must retain the above copyright
   #   notice, this list of conditions and the following disclaimer.
   # * Redistributions in binary form must reproduce the above copyright
   # notice, this list of conditions and the following disclaimer in the
   # documentation and/or other materials provided with the distribution.
   # * Neither the name of Kurt Rathjen nor the
   # names of its contributors may be used to endorse or promote products
   # derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY KURT RATHJEN ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL KURT RATHJEN BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
import urllib2
import getpass
import platform
import threading
__all__ = ['Analytics']

class Analytics:

    def __init__(self, tid, name = 'PacakgeName', version = '1.0.0'):
        """
        @type name: str
        @type version: str
        """
        self._tid = tid
        self._name = name
        self._enabled = True
        self._version = version

    def setEnabled(self, enable):
        """
        @type enable: bool
        """
        self._enabled = enable

    def isEnabled(self):
        """
        @rtype: bool
        """
        return self._enabled

    def logEvent(self, name, value):
        """
        @type name: str
        @type value: str
        """
        try:
            if self.isEnabled():
                url = self._url + '&t=event&ec=' + name + '&ea=' + value
        except Exception:
            pass

    def logScreen(self, name):
        """
        @type name: str
        """
        try:
            if self.isEnabled():
                url = self._url + '&t=appview&cd=' + name
        except Exception:
            pass

    @property
    def cid(self):
        """
        @rtype: str
        """
        return getpass.getuser() + '-' + platform.node()

    @property
    def _url(self):
        """
        @rtype: str
        """
        url = 'http://www.google-analytics.com/collect?v=1&ul=en-us&a=448166238&_u=.sB&_v=ma1b3&qt=2500&z=185'
        return url + '&tid=' + self._tid + '&an=' + self._name + '&cid=' + self.cid + '&av=' + self._version

    @staticmethod
    def send(url):
        """
        @type url: str
        """
        t = threading.Thread(target=Analytics._send, args=(url,))
        t.start()

    @staticmethod
    def _send(url):
        """
        @type url: str
        """
        try:
            url = url.replace(' ', '')
            f = urllib2.urlopen(url, None, 1.0)
        except Exception as e:
            pass
