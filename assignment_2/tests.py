import unittest
from ass2_base import parse_reply
from ass2_base import parse_ipv4


class Tests(unittest.TestCase):
    reply_expected = [{"id": b'ACAC', "ipv4": "65.254.242.180"}]
    question = b'\x03www\x08mydomain\x03com\x00\x00\x01\x00\x01'

    def test_reply_mydomain(self):
        data = b'\xac\xac\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\x03www\x08mydomain\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x05\x00\x01\x00\x00\x02W\x00\x02\xc0\x10\xc0\x10\x00\x01\x00\x01\x00\x00\x02W\x00\x04A\xfe\xf2\xb4'

        expected = self.reply_expected[0]["ipv4"]
        self.assertEqual(expected, parse_reply(data, self.question)[0]["ipv4"], "wrong ipv4 addr")

    def test_ipv4(self):
        ip_bytes = bytearray(b'A\xfe\xf2\xb4')
        expected = "65.254.242.180"

        self.assertEqual(expected, parse_ipv4(ip_bytes))
if __name__ == '__main__':
    unittest.main()