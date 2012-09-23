from __future__ import division
import math


needed_bits = lambda n: int(math.ceil(math.log(n, 2)))

MAX_VALUES_BYTE = 64
MAX_BITS = needed_bits(MAX_VALUES_BYTE)


class EncoderException(Exception):
    pass


class Encoder(object):

    def __init__(self, base=64, start_char='0'):
        self.base = base
        # number of bits needed to represent a number in the given base:
        numbits = needed_bits(base)
        self.digits = int(math.ceil(numbits / MAX_BITS))
        self.start_char = start_char

    def encode(self, position):
        n = position
        encoded = ''
        for i in range(0, self.digits):
            next_char = chr(n % MAX_VALUES_BYTE + ord(self.start_char))
            encoded = next_char + encoded
            n = n // MAX_VALUES_BYTE
        return encoded

    def decode(self, encoded):
        value = 0
        if len(encoded) != self.digits:
            raise EncoderException(
                    'Length of encoded value {0} should be {1}'
                    .format(encoded, self.digits))
        for i in range(0, self.digits):
            next_digit = (ord(encoded[i]) - ord(self.start_char))
            value = value * MAX_VALUES_BYTE + next_digit
        return value
