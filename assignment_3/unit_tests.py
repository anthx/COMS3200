import unittest
import binascii
from . ass3 import Response
from . ass3 import calc_checksum


class Tests(unittest.TestCase):
    def test_ttl_exceeded(self):
        data = binascii.unhexlify("45c05a00be5f0000400102640a5352010a5352650b00ef7e00000000450052006371000001010df60a53526568478345080065a0acac0001000008090a0b0c0d0e0f1011121314151617001018191a1b1c1d1e1f2021222324252627002028292a2b2c2d2e2f3031323334353637")
        a = Response(data)
        self.assertEqual(11, a.type, "Should be Type 11 for TTL Expired")
        self.assertEqual(0, a.code, "Should be Code 0 for TTL Expired")
        self.assertEqual("10.83.82.1", a.source, "incorrect source")

    def atest_checksum(self):
        data = bytearray(b'\x08\x00\x00\x00\xac\xac\x00\x01\x00\x00\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x00\x10\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'\x00 ()*+,-./01234567')
        actual = calc_checksum(data)
        expected = b'\x60\x1f'
        self.assertEqual(expected, actual, "checksum doesn't match")

    def test_checksum(self):
        data = bytearray(b'\x45\x00\x00\x3c\x1c\x46\x40\x00\x40\x06\x00\00\xac\x10\x0a\x63\xac\x10\x0a\x0c')
        actual = calc_checksum(data)
        expected = b'\xb1\xe6'
        self.assertEqual(expected, actual, "checksum doesn't match")
