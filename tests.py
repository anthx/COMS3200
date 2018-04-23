import unittest
from assignment1 import http_return_code
# from assignment1 import request_date
# from assignment1 import request_last_modified
# from assignment1 import request_encoding


class Tests(unittest.TestCase):

    string = """HTTP/1.1 200 OK
Server: nginx/1.8.1
Date: Sun, 11 Mar 2018 10:32:00 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 22 Mar 2016 11:25:26 GMT
Connection: close
Vary: Accept-Encoding
ETag: "56f12ba6-264"
Cache-Control: public
X-Served-By: 10.138.100.77
Accept-Ranges: bytes"""

    def test_http_200(self):
        string = "HTTP/1.0 200 OK"
        expected = (200, "OK")
        self.assertEqual(expected, http_return_code(string))

    def test_http_404(self):
        string = "HTTP/1.1 404 Not Found"
        expected = (404, "Not Found")
        self.assertEqual(expected, http_return_code(string))

    def test_http_404_with_content(self):
        string = "HTTP/1.1 500 Server Error\r\nOther Stuff"
        expected = (500, "Server Error")
        self.assertEqual(expected, http_return_code(string))

    def test_date_content(self):
        string = "Date: Sun, 11 Mar 2018 04:05:14 GMT\r\nOther Stuff"
        expected = "Sun, 11 Mar 2018 04:05:14 GMT"
        self.assertEqual(expected, request_date(string))

    def test_modifed_content(self):
        string = "Last-Modified: Sun, 11 Mar 2018 04:05:14 GMT\r\nOther Stuff"
        expected = "Tue, 22 Mar 2016 11:25:26 GMT"
        self.assertEqual(expected, request_last_modified(self.string))

    def test_content_encoding(self):
        string = "Content-Encoding: GZIP\r\nOther Stuff"
        expected = "GZIP"
        self.assertEqual(expected, request_encoding(string))

    def test_encoding_none(self):
        string = "Date: Sun 11 March\r\nOther Stuff"
        expected = "None Specified"
        self.assertEqual(expected, request_encoding(self.string))