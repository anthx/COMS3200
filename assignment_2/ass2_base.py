# this is the basic command line app and base code
import socket
import sys
import binascii
from bitstring import BitArray

"""
The first 12 bytes is the header section, which has a number of fields. 
The first field is a 16-bit number that identifies the query. This identifier is
 copied into the reply message to a query, allowing the client to match received
  replies with sent queries. There are a number of flags in the flag field. 
  A 1-bit query/reply flag indicates whether the message is a query (0) or a 
  reply (1). 
  A 1-bit authoritative flag is set in a reply message when a DNS 
  server is an authoritative server for a queried name. 
  A 1-bit recursion-desired flag is set when a client (host or DNS server) 
  desires that the DNS server perform recursion when it doesn’t have the record.
   A 1-bit recursion- available field is set in a reply if the DNS server 
   supports recursion. In the header, there are also four number-of fields. 
   These fields indicate the number of occurrences of the four types of 
   data sections that follow the header.
   """
"""
The question section contains information about the query that is being made.
 This section includes (1) a name field that contains the name that is being 
 queried, and (2) a type field that indicates the type of question being asked 
 about the name—for example, a host address associated with a name (Type A) or 
 the mail server for a name (Type MX).
• In a reply from a DNS server, the answer section contains the resource records
 for the name that was originally queried. Recall that in each resource record 
 there is the Type (for example, A, NS, CNAME, and MX), the Value, and the TTL. 
 A reply can return multiple RRs in the answer, since a hostname can have 
 multiple IP addresses (for example, for replicated Web servers, as discussed 
 earlier in this section).
• The authority section contains records of other authoritative servers.
• The additional section contains other helpful records. For example, 
the answer field in a reply to an MX query contains a resource record providing 
the canonical hostname of a mail server. The additional section contains a 
Type A record providing the IP address for the canonical hostname of the mail 
server.
"""
# message = "AA AA 01 00 00 01 00 00 00 00 00 00 " \
# "07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 01 00 01"
# message = message.replace(" ", "").replace("\n", "")
# a = binascii.unhexlify(message)
# print(a)


def host_question(host:str, record:str = "A") -> bytearray:
    """
    creates DNS question from host and record
    :param host: str, the host
    :param record: str, record type
    :return: bytearray of hex
    """
    data = bytearray()
    qname = bytearray()
    qtype = bytes()
    qclass = b'\x00\x01'
    for label in host.split('.'):
        qname.extend(bytes([len(label)]))
        qname.extend(bytes(label, "utf-8"))
    # Finish the QNAME with 00
    qname.extend(bytes([0]))

    if record == "A":
        qtype = b'\x00\x01'

    data = bytearray(qname)
    print(data)

    data.extend(qtype)
    data.extend(qclass)
    print("question", data)
    return data


def parse_reply(data: bytes, question_bytes: bytes):
    """
    Takes DNS response and parses it
    :param data:
    :param question: the original domain/ip to lookup
    :return:
    """
    bytes_array = bytearray(data)

    answer = {}
    answer["id"] = bytes_array[0:2]
    flags = BitArray(bytes_array[2:4])
    answer_count: int = int.from_bytes(bytes_array[6:8], "big")
    start_of_answers = 12 + len(question_bytes)
    answers = bytes_array[start_of_answers:]
    # 11 or 00 in binary is the start the record
    name = BitArray(answers[0:2])
    if name.bin.startswith("11"):
        pass
    # pointer = BitArray(name.bin[2:])
    stuff = {"ipv4": "0.0.0.0"}
    return stuff


def query_dns(dns: str, host: str) -> dict:
    """
    Queries the DNS server for the host given
    :param dns: string of ip
    :param host: string on address
    :return: dict of data
    """

    dry_run = False
    address = (dns, 53)
    qr = 0
    op_code: int = 0
    tc = 0
    rd = 1
    qd_count = 1
    message = bytearray(b'\xAC\xAC')
    print(message.__len__())
    flags = BitArray("0b"+
                     format(qr, 'b')+
                     format(op_code,'04b')+
                     # AA
                     format(0, 'b')+
                     format(tc, 'b')+
                     format(rd, 'b')+
                     # 3 Reserved bits
                     format(0, 'b') +
                     format(0, 'b') +
                     format(0, 'b') +
                     # RA
                     format(0, 'b') +
                     # RCODE
                     format(0, '04b'))

    message.extend(flags.bytes)
    print(message.__len__())
    # QDCOUNT
    if qd_count == 1:
        message.extend(b'\x00\x01')
    # ANCOUNT
    message.extend(b'\x00\x00')
    # NSCOUNT
    message.extend(b'\x00\x00')
    # ARCOUNT
    message.extend(b'\x00\x00')

    print("header length:", message.__len__())
    print(message)
    # Make the query

    query = host_question(host, "A")
    message.extend(query)
    print(message)
    print("message length: ", message.__len__())

    if not dry_run:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(message, address)

        data, _ = s.recvfrom(2048)
        print(data)
    answer = {"ipv4": "0.0.0.0"}
    return answer


def runner():
    query_dns("8.8.8.8", "www.mydomain.com")


if __name__ == '__main__':
    runner()