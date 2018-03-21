from urllib.parse import urlparse
import socket
import sys
import re
from dateutil.parser import parse
from dateutil.tz import tzoffset

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


def gmt_aest(time_str: str) -> str:
    """
    converts a string representation of a date/time to AEST
    :param time_str: time to convert as string
    :return: converted time as string
    """
    time = parse(time_str)
    aest = tzoffset("AEST", 36000)
    if time.tzname() == "GMT" or time.tzname() == "UTC":
        result = time.astimezone(aest)
    else:
        result = time
    return result.strftime("%a, %d %b %Y  %H:%M:%S %Z")


def main():
    print("HTTP Protocol Analyzer, Written by Anthony Carrick, #########")
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("URL to Retrieve: ")
    reply_code = -1
    i = 1
    prev_host = ""
    while reply_code in {301, 302, -1}:
        print(i)
        reply_code, url, prev_host = request_process(url, prev_host)
        i += 1
    print("Finished")


def request_process(url: str, prev_host="") -> (int, str):
    host = ""
    port = 80
    host_path = process_url(url)
    if host_path[0] == "":
        host = prev_host
    else:
        host = host_path[0]
    address = (host, port)
    server_ip = ""
    server_port = ""
    client_ip = ""
    client_port = ""
    reply_code = 0
    reply_code_meaning = ""
    date = 0
    last_modified = 0
    content_encoding = ""
    conn = 0
    moved_to = ""
    try:
        conn = socket.socket()
        conn.connect(address)
        data = bytes(
            f"HEAD {host_path[1]} HTTP/1.0\r\n"
            f"Host: {host}\r\n\r\n", "utf-8")
        # print(data)
        try:
            conn.sendall(data)
        except socket.error:
            print('Send failed')
            conn.close()
            sys.exit()
        # conn.sendall(data)
        reply = conn.recv(4096)
        # print(reply.decode())
        client_ip, client_port = conn.getsockname()
        server_ip, server_port = conn.getpeername()

        for line in reply.decode().splitlines():
            if line.startswith("Date: "):
                date = gmt_aest(line[6:])
            if line.startswith("Last-Modified: "):
                last_modified = gmt_aest(line[15:])
            if line.startswith("Accept-Encoding: "):
                content_encoding = line[17:]
            if line.startswith("Location: "):
                moved_to = line[10:]

            if last_modified == 0:
                last_modified = "Not Specified"
            if content_encoding == "":
                content_encoding = "None"
        reply_code, reply_code_meaning = http_return_code(reply.decode())

        # content_encoding = request_encoding(reply.decode())
        # date = request_date(reply.decode())
        # last_modified = request_last_modified(reply.decode())
        output = f"""URL Requested: {url} 
IP Address, # Port of the Server:  {server_ip} , {server_port} 
IP Address # Port of this Client:  {client_ip} , {client_port} 
Reply Code: {reply_code} 
Reply Code Meaning:  {reply_code_meaning}. 
Date: {date}  
Last-Modified: {last_modified}  
Content-Encoding:  {content_encoding}
Moved to: {moved_to} 
        """

        print(output)
        conn.close()
    # except socket.error:
    #     print("Failed to create socket")
    #     sys.exit()
    except socket.gaierror:
        print("Couldn't resolve host. Exiting")
        sys.exit()
    finally:
        conn.close()
        return reply_code, moved_to, host_path[0]


if __name__ == '__main__':
    main()