# Anthony Carrick
from bitstring import BitArray
import socket
import sys
import random
import binascii

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
        result.append(int(octet))
    return result


def calc_checksum(data: bytearray) -> bytes:
    pass


class Response(object):
    """
    holds response stuff
    """
    def __init__(self, response_bytes):
        self._response_bytes = response_bytes
        self.type = 0
        self.code = 0
        self._icmp_part = bytearray

        # the .recv() method when used with RAW sockets seems to also include
        # IP header.
        # Can either skip over the first 20 bytes or
        # confirm the length (probably better choice)

        ip_header_length: int = 0
        ip_ver_len = BitArray(self._response_bytes[0:1])
        ip_header_length = int(ip_ver_len[4:].bin, 2) * 4

        self._icmp_part = self._response_bytes[ip_header_length:]
        self.type = int(self._icmp_part[0])
        self.code = int(self._icmp_part[1])


class Ping(object):
    """
    Handles sending a ping and receiving the response
    """
    def __init__(self, host: str, ttl: int = 64):
        self._host = host
        self._response = bytearray
        self._RTT = ""
        self._TTL = ttl
        self._total_length: int = 84
        self._my_ip = ""
        self._host_ip = ""
        self._ping_packet = bytearray
        self.response = None
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
        ip_ver_hrd_size = BitArray("0b01000101").bytes
        tos = int(0).to_bytes(1, "big")
        # total_length is measured in octets and is 2 octets long
        total_length = self._total_length.to_bytes(2, "big")
        # I just pick a number
        packet_id = int(333).to_bytes(2, "big")
        flags_frag_offset = int(0).to_bytes(2, "big")
        ttl = self._TTL.to_bytes(1, "big")
        protocol = b'\x01'
        checksum = int(0).to_bytes(1, "big")
        source_ip = ipv4_to_bytearray(self._my_ip)
        destination_ip = ipv4_to_bytearray(self._host_ip)

        result = bytearray()
        result.extend(ip_ver_hrd_size)
        result.extend(tos)
        result.extend(total_length)
        result.extend(packet_id)
        result.extend(flags_frag_offset)
        result.extend(ttl)
        result.extend(protocol)
        result.extend(checksum)
        result.extend(source_ip)
        result.extend(destination_ip)

        return result

    def icmp_packet(self) -> bytearray:
        """
        creates an ICMP Header
        :return:
        """
        type = int(8).to_bytes(1, "big")
        code = int(0).to_bytes(1, "big")
        checksum = b'\x65\xa0'
        identifier = b'\xAC\xAC'
        sequence = b'\x00\x01'
        data = binascii.unhexlify("000008090a0b0c0d0e0f1011121314151617001018191a1b1c1d1e1f2021222324252627002028292a2b2c2d2e2f3031323334353637")

        result = bytearray()
        result.extend(type)
        result.extend(code)
        result.extend(checksum)
        result.extend(identifier)
        result.extend(sequence)
        result.extend(data)
            
        return result

    def generate_packet(self):
        ip_header = self.ip_header()
        ping = bytearray()
        # ping.extend(ip_header)
        ping.extend(self.icmp_packet())

        self._ping_packet = ping

    def print(self):
        print(binascii.hexlify(self._response))

    def handle_response(self):
        """
        handles response packet
        :return: None
        """
        self.response = Response(self._response)
        if self.response.type == 0:
            # stuff to do with the response. Not sure yet
            pass

    def send_recv(self):
        """
        Sends an ICMP echo request and receives the response
        """
        try:
            address = (socket.gethostbyname(self._host), 0)
            print("open raw socket")
            soc = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
            soc.setsockopt(socket.SOL_IP, socket.IP_TTL, self._TTL)
            print("send")
            soc.sendto(self._ping_packet, address)
            print("receive")
            self._response = bytearray(soc.recv(4096))
            self.handle_response()
        except socket.error as err:
            print("Can't make socket:", err)
            exit(0)


def trace_ping():
    ttl_incr = 1
    while True:
        a_ping = Ping("www.abc.net.au", ttl_incr)
        a_ping.generate_packet()
        a_ping.send_recv()
        a_ping.print()
        print(a_ping.response.type, ttl_incr)
        ttl_incr +=1
        if a_ping.response == None:
            break


if __name__ == "__main__":
    trace_ping()