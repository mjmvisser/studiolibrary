#Embedded file name: C:/Users/hovel/Dropbox/packages/studiolibrary/1.12.1/build27/studiolibrary\core\shortuuid.py
"""
Copyright (c) 2011, Stochastic Technologies
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

Neither the name of Stochastic Technologies nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import binascii
import math
import os
import uuid as _uu
__all__ = ['ShortUUID']

class ShortUUID(object):

    def __init__(self, alphabet = None):
        if alphabet is None:
            alphabet = list('1234567890ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz')
        self.set_alphabet(alphabet)

    def _num_to_string(self, number, pad_to_length = None):
        """
        Convert a number to a string, using the given alphabet.
        """
        output = ''
        while number:
            number, digit = divmod(number, self._alpha_len)
            output += self._alphabet[digit]

        if pad_to_length:
            remainder = max(pad_to_length - len(output), 0)
            output = output + self._alphabet[0] * remainder
        return output

    def _string_to_int(self, string):
        """
        Convert a string to a number, using the given alphabet..
        """
        number = 0
        for char in string[::-1]:
            number = number * self._alpha_len + self._alphabet.index(char)

        return number

    def encode(self, uuid, pad_length = 22):
        """
        Encodes a UUID into a string (LSB first) according to the alphabet
        If leftmost (MSB) bits 0, string might be shorter
        """
        return self._num_to_string(uuid.int, pad_to_length=pad_length)

    def decode(self, string):
        """
        Decodes a string according to the current alphabet into a UUID
        Raises ValueError when encountering illegal characters
        or too long string
        If string too short, fills leftmost (MSB) bits with 0.
        """
        return _uu.UUID(int=self._string_to_int(string))

    def uuid(self, name = None, pad_length = 22):
        """
        Generate and return a UUID.
        If the name parameter is provided, set the namespace to the provided
        name and generate a UUID.
        """
        if name is None:
            uuid = _uu.uuid4()
        elif 'http' not in name.lower():
            uuid = _uu.uuid5(_uu.NAMESPACE_DNS, name)
        else:
            uuid = _uu.uuid5(_uu.NAMESPACE_URL, name)
        return self.encode(uuid, pad_length)

    def random(self, length = 22):
        """
        Generate and return a cryptographically-secure short random string
        of the specified length.
        """
        random_num = int(binascii.b2a_hex(os.urandom(length)), 16)
        return self._num_to_string(random_num, pad_to_length=length)[:length]

    def get_alphabet(self):
        """Return the current alphabet used for new UUIDs."""
        return ''.join(self._alphabet)

    def set_alphabet(self, alphabet):
        """Set the alphabet to be used for new UUIDs."""
        new_alphabet = list(sorted(set(alphabet)))
        if len(new_alphabet) > 1:
            self._alphabet = new_alphabet
            self._alpha_len = len(self._alphabet)
        else:
            raise ValueError('Alphabet with more than one unique symbols required.')

    def encoded_length(self, num_bytes = 16):
        """
        Returns the string length of the shortened UUID.
        """
        factor = math.log(256) / math.log(self._alpha_len)
        return int(math.ceil(factor * num_bytes))
