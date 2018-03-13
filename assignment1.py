from urllib.parse import urlparse
import socket
import sys
import re
from datetime import datetime
from dateutil.tz import tzutc, tzlocal
from typing import *

# Anthony Carrick -


def process_url(url):
    """
    Returns a tuple of hostname, path
    :return: tuple
    """
    parsed = urlparse(url)
    if parsed.scheme:
        return parsed.netloc, parsed.path
    else:
        host_part = parsed.path
        hostname = host_part.partition("/")[0]
        path = "/" + host_part.partition("/")[2]
        return hostname, path


def http_return_code(res_data) -> (int, str):
    """
    Extracts the HTTP code and meaning from a string
    :param res_data: string
    :return: tuple of code and meaning
    """

    start = re.search("[0-9]{3}", res_data).start()
    end_of_line = res_data.find("\r\n")
    code = int(res_data[start:start+3])
    if end_of_line == -1:
        end_of_line = len(res_data)
    meaning = res_data[start+4:end_of_line]
    return code, meaning


# def request_date(res_data) -> str:
#     """
#     Extracts Date: from string
#     :param res_data:
#     :return: string of date
#     """
#     start = re.search("Date: ", res_data).start()
#     end_of_line = res_data.find("\r\n")
#     if end_of_line == -1:
#         end_of_line = len(res_data)
#     date = res_data[start + 6:end_of_line]
#     return date


# def request_last_modified(res_data) -> str:
#     """
#     Extracts Last Modified: from string
#     :param res_data:
#     :return: string of date
#     """
#     # use str.splitlines() to loop over each line
#     start = re.search("Last-Modified: ", res_data).start()
#     end_of_line = res_data.find("\n")
#     if end_of_line == -1:
#         end_of_line = len(res_data)
#     date = res_data[start + 15:end_of_line]
#     return date


# def request_encoding(res_data) -> Union[str,None]:
#     """
#     Extracts Content-Encoding: from string
#     :param res_data:
#     :return: string of date
#     """
#     try:
#         start = re.search("Content-Encoding: ", res_data).start()
#     except AttributeError:
#         return "None Specified"
#     end_of_line = res_data.find("\r\n")
#     if end_of_line == -1:
#         end_of_line = len(res_data)
#     enc = res_data[start + 18:end_of_line]
#     return enc


def main():
    # url = input("URL to Retrieve: ")
    url = "www.google.com.au"
    host = ""
    port = 80

    host_path = process_url(url)

    address = (host_path[0], port)
    server_ip = ""
    server_port = ""
    client_ip = ""
    client_port = ""
    reply_code = 0
    reply_code_meaning = ""
    date = 0
    last_modified = 0
    content_encoding = ""

    try:
        conn = socket.socket()
        conn.connect(address)
        data = bytes(
            f"GET {host_path[1]} HTTP/1.0\r\n\r\n"
            f"Host {host_path[0]}\r\n","utf-8")
        print(data)
        try:
            conn.sendall(data)
        except socket.error:
            print('Send failed')
            conn.close()
            sys.exit()

        conn.sendall(data)
        reply = conn.recv(16384)
        print(reply.decode())
        client_ip, client_port = conn.getsockname()
        server_ip, server_port = conn.getpeername()

        for line in reply.decode().splitlines():
            if line.startswith("Date: "):
                date = line[6:]
            if line.startswith("Last-Modified: "):
                last_modified = line[15:]
            if line.startswith("Content-Encoding: "):
                content_encoding = line[18:]

        reply_code, reply_code_meaning = http_return_code(reply.decode())

        # content_encoding = request_encoding(reply.decode())
        # date = request_date(reply.decode())
        # last_modified = request_last_modified(reply.decode())
        output = f"""
        HTTP Protocol Analyzer, Written by Anthony Carrick, #########
        URL Requested: {url} 
        IP Address, # Port of the Server:  {server_ip} , {server_port} 
        IP Address # Port of this Client:  {client_ip} , {client_port} 
        Reply Code: {reply_code} 
        Reply Code Meaning:  {reply_code_meaning}. 
        Date: {date} (please convert times to AEST if they are in GMT, otherwise leave them as they are) 
        Last-Modified: {last_modified} similar format  (if appropriate to the response) 
        Content-Encoding:  {content_encoding}
        Moved to:      (if appropriate to the response) 
        """

        print(output)
        conn.close()
    # except socket.error:
    #     print("Failed to create socket")
    #     sys.exit()
    except socket.gaierror:
        print("Couldn't resolve host. Exiting")
        sys.exit()

if __name__ == '__main__':
    main()