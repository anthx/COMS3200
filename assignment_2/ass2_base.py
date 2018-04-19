# this is the basic command line app and base code
import socket
import sys
import binascii
from bitstring import BitArray
from binascii import unhexlify
from binascii import hexlify

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
    if record not in ["A", "AAAA"]:
        raise ValueError("Unsupported RR given.")
    if record == "A":
        qtype = b'\x00\x01'
    if record == "AAAA":
        qtype = b'\x00\x1c'
    data = bytearray(qname)
    print(data)

    data.extend(qtype)
    data.extend(qclass)
    print("question", data)
    return data


def parse_ipv4(ip_bytes: bytearray):
    ip = ""
    for byte in ip_bytes:
        ip += str(byte)
        ip += "."
    ip = ip[0:len(ip)-1]
    return ip


def parse_ipv6(ip_bytes: bytearray):
    ip = ""
    for pair in range(0, 15, 2):
        byte_pair = ip_bytes[pair:pair+2]
        hex_str = str(hexlify(byte_pair))
        hex_str = hex_str[2:-1]
        ip += hex_str
        ip += ":"
        # if pair == 14:
        #     ip += ":"
    ip = ip[0:len(ip)-1]
    return ip


def parse_reply(data: bytearray, question_bytes: bytearray) -> list:
    """
    Takes DNS response and parses it
    :param data:
    :param question_bytes: the original domain/ip to lookup
    :param question_bytes: the question we sent so we have it as a reference
    :return:
    """
    stuff = []
    bytes_array = bytearray(data)

    answer = dict()
    answer["id"] = bytes_array[0:2]
    flags = BitArray(bytes_array[2:4])
    answer_count: int = int.from_bytes(bytes_array[6:8], "big")
    start_of_answers = 12 + len(question_bytes)
    answers = bytes_array[start_of_answers:]
    # 11 or 00 in binary is the start the record
    byte_offset = 0
    for ans in range(answer_count):
        this_answer = {}
        name = BitArray(answers[byte_offset+0:byte_offset+2])
        if name.bin.startswith("11"):
            pass
            # pointer = int.from_bytes(BitArray(name.bin[2:]).bytes, "big")

        # each answer consists of 10 bytes before the RDLENGTH
        type = int.from_bytes(answers[byte_offset+2:byte_offset+4], "big")
        this_answer["type"] = type
        klass = int.from_bytes(answers[byte_offset+4:byte_offset+6], "big")

        rdlength = int.from_bytes(answers[byte_offset+10:byte_offset+12], "big")
        rdata = answers[byte_offset+12:byte_offset+12+rdlength]
        byte_offset = byte_offset + rdlength + 12
        if type == 1:
            this_answer["ipv4"] = parse_ipv4(rdata)
        if type == 5:
            this_answer["cname"] = 0
        if type == 28:
            this_answer["ipv6"] = parse_ipv6(rdata)
        stuff.append(this_answer)
        print("")
    return stuff


def query_dns(dns: str, host: str, qtype: str) -> list:
    """
    Queries the DNS server for the host given
    :param dns: string of ip
    :param host: string of address
    :param: qtype: string of Question Type
    :return: dict of data
    """
    answer = []
    dry_run = False
    address = (dns, 53)
    message, query = create_request_message(host, qtype)

    if not dry_run:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(message, address)

        data, _ = s.recvfrom(2048)
        print(data)
        answer = parse_reply(data, query)
    print(answer)
    return answer


def create_request_message(host, qtype):
    """
    generates requests for a DNS request
    :param host: the host to query for
    :param qtype: the type of request
    :return: 
    """
    qr = 0
    op_code: int = 0
    tc = 0
    rd = 1
    qd_count = 1
    message = bytearray(b'\xAC\xAC')
    print(message.__len__())
    flags = BitArray("0b" +
                     format(qr, 'b') +
                     format(op_code, '04b') +
                     # AA
                     format(0, 'b') +
                     format(tc, 'b') +
                     format(rd, 'b') +
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
    query = host_question(host, qtype)
    message.extend(query)
    print(message)
    print("message length: ", message.__len__())
    return message, query


def runner():
    query_dns("8.8.8.8", "google.com", "AAAA")


if __name__ == '__main__':
    runner()