from __future__ import division
import math


needed_bits = lambda n: int(math.ceil(math.log(n, 2)))

MAX_VALUES_BYTE = 64
MAX_BITS = needed_bits(MAX_VALUES_BYTE)


class EncoderException(Exception):
    pass


class Encoder(object):

    def __init__(self, base=10, start_char='0'):
        self.base = base
        # number of bits needed to represent a number in the given base:
        numbits = needed_bits(base)
        self.digits = int(math.ceil(numbits / MAX_BITS))
        self.start_char = start_char

    def encode(self, position):
        if self.digits != 1:
            raise EncoderException('More than 1 digit per level not supported')
        return chr(position + ord(self.start_char))

    def decode(self, encoded):
        if self.digits != 1:
            raise EncoderException('More than 1 digit per level not supported')
        return ord(encoded) - ord(self.start_char)
