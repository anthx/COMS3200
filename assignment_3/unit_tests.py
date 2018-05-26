import unittest
import binascii
from . ass3 import Response


class Tests(unittest.TestCase):
    def test_ttl_exceeded(self):
        data = binascii.unhexlify("45c05a00be5f0000400102640a5352010a5352650b00ef7e00000000450052006371000001010df60a53526568478345080065a0acac0001000008090a0b0c0d0e0f1011121314151617001018191a1b1c1d1e1f2021222324252627002028292a2b2c2d2e2f3031323334353637")
        a = Response(data)
        self.assertEqual(11, a.type, "Should be Type 11 for TTL Expired")
        self.assertEqual(0, a.code, "Should be Code 0 for TTL Expired")
        self.assertEqual("10.83.82.1", a.source, "incorrect source")
