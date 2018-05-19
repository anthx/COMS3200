# Anthony Carrick
from bitstring import BitArray
import socket
import sys
import random

"""

You can resolve the IP address using socket routines like “gethostbyname”.
You not only need to confirm the host is reachable, and measure the time between
 send and receive, you need to count the number of hops to the destination, by 
 setting the TTL to 1,2,3, etc until you get a ping reply (rather than a 
 lifetime exceeded message).
 
Also once you get a reply send 2 more packets to the end host (3 in total), and 
average the delay time to the nearest millisecond. You only need to do the 
“trace route” steps for the first packet.

After 1 second you can time out and assume that host doesn’t reply to pings.
Your program should output the following to the console, or to a log file 
(or both) so that you can capture the output for upload with your program. 
Because the deadline is last day of semester, and we can’t do assessment like 
demos in Swat Vac, it will be easier to upload evidence of correct operation 
(similar to assignment 1), rather than demos."""

"""
The program output should look something like:
Pyping by A. Student
Sending 3 PINGs to host.uni.edu.au, IP 123.124.125.1 \ 
    3 replies received with average 22 ms, 14 hops.
OR
Request timed out
OR
Not a valid host name
"""


def ipv4_to_bytearray(ip: str):
    result = bytearray()
    for octet in ip.split('.'):
        result.append(octet)
    return result


class Ping(object):
    """
    Handles sending a ping and receiving the response
    """
    def __init__(self, host: str, ttl: int = 64):
        self._host = host
        self._response = bytes
        self._RTT = ""
        self._TTL = ttl
        self._total_length: int = 0
        self._my_ip = ""
        self._host_ip = ""
        try:
            self._host_ip = socket.gethostbyname(host)
        except socket.gaierror:
            print('Hostname could not be resolved. Exiting')
            sys.exit()
        try:
            conn_for_ip = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._my_ip, _ = conn_for_ip.getsockname()
            conn_for_ip.close()
        except socket.gaierror:
            print("Couldn't open socket. Exiting")
            sys.exit()

    def ip_header(self) -> bytearray:
        """
        Makes and returns the IP Header
        http://www.zytrax.com/tech/protocols/tcp.html#icmp
        :return: bytearray: the header
        """
        # version 4 then 20 octets
        ip_ver_hrd_size = BitArray("01000101").tobytes()
        tos = b'00'
        # total_length is measured in octets and is 2 octets long
        total_length = self._total_length.to_bytes(2, "big")
        # I just pick a number
        packet_id = bytes(random.randint(1, 65000))
        flags_frag_offset = b'0000'
        ttl = self._TTL.to_bytes(1, "big")
        protocol = b'01'
        checksum = b'0000'
        source_ip = ipv4_to_bytearray(self._my_ip)
        destination_ip = ipv4_to_bytearray(self._host_ip)

        result = bytearray.append()

    def send_recv(self):
        """
        Sends an ICMP echo request and receives the response

        """
        ping = bytes()
        try:
            address = (socket.gethostbyname(self._host), 0)
            soc = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            # soc.setsockopt(socket.IP_HDRINCL, True)
            soc.sendto(ping, address)
        except socket.error:
            print("Can't make socket")
            exit(0)
