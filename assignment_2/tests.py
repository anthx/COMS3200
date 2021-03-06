import unittest
from ass2_base import parse_reply
from ass2_base import parse_ipv4
from ass2_base import parse_ipv6
from ass2_base import parse_mx
from ass2_base import parse_label_format
from ass2_base import parse_cname
from binascii import unhexlify
from binascii import hexlify


class Tests(unittest.TestCase):
    reply_expected = [{"id": b'ACAC', "ipv4": "65.254.242.180"}]
    question = b'\x03www\x08mydomain\x03com\x00\x00\x01\x00\x01'

    def not_test_reply_mydomain(self):
        data = b'\xac\xac\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\x03www\x08mydomain\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x05\x00\x01\x00\x00\x02W\x00\x02\xc0\x10\xc0\x10\x00\x01\x00\x01\x00\x00\x02W\x00\x04A\xfe\xf2\xb4'

        expected = self.reply_expected[0]["ipv4"]
        self.assertEqual(expected, parse_reply(data, self.question)[0]["ipv4"], "wrong ipv4 addr")

    def test_ipv4(self):
        ip_bytes = bytearray(b'A\xfe\xf2\xb4')
        expected = "65.254.242.180"
        self.assertEqual(expected, parse_ipv4(ip_bytes))

    def test_ipv6(self):
        ip_bytes = unhexlify("2404680040060808000000000000200e")
        expected = "2404:6800:4006:808::200e"
        self.assertEqual(expected, parse_ipv6(ip_bytes))

    def test_ipv6_1(self):
        ip_bytes = unhexlify("24072e0006020303be8bd51e6a959b72")
        expected = "2407:2e00:602:303:be8b:d51e:6a95:9b72"
        self.assertEqual(expected, parse_ipv6(ip_bytes))

    def test_mx(self):
        mx_bytes = (bytearray(b'\x00\n\x05aspmx\x01l\xc0\x0c'))
        expected = "aspmx.l.google.com."
        self.assertEqual(expected, parse_mx(mx_bytes))

    def test_label_format(self):
        label_bytes = bytearray(b'\x05manna\x04eait\x02uq\x03edu\x02au\x00')
        expected = "manna.eait.uq.edu.au"
        self.assertEqual(expected, parse_label_format(label_bytes))

    def test_cname(self):
        data = b'\xac\xac\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\x03www\x08mydomain\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x05\x00\x01\x00\x00\x02W\x00\x02\xc0\x10\xc0\x10\x00\x01\x00\x01\x00\x00\x02W\x00\x04A\xfe\xf2\xb4'
        expected = "mydomain.com."
        self.assertEqual(expected, parse_cname(data))


if __name__ == '__main__':
    unittest.main()