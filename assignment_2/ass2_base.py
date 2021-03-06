# this is the basic command line app and base code
#Anthony Carrick
import socket
import sys
import binascii
from bitstring import BitArray
from binascii import unhexlify
from binascii import hexlify
import re
import dnslib

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


class CompleteResult(object):

    def __init__(self, result: dict):
        self._result = result

    def __str__(self):
        string = f"Host: {self._result.get('host')}"
        if "cname" in self._result:
            string += "\n" + \
                      f"Canonical Name: {self._result.get('cname', 'None')}"
        if "ipv4" in self._result:
            ips = ', '.join(self._result['ipv4'])
            string += "\n" + f"IPv4: {ips}"
        if "ipv6" in self._result:
            string += "\n" + f"IPv6: {self._result.get('ipv6','None')}"
        if "reverse" in self._result:
            string += "\n" + f"Name: {self._result.get('reverse','None')}"
        if "mx" in self._result:
            string += "\n" + f"MX: {', '.join(self._result['mx'])}"
        return string


def host_question(host: str, record: str = "A") -> bytearray:
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

    if re.search("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}", host):
        record = "PTR"
    if record not in ["A", "AAAA", "MX", "PTR"]:
        raise ValueError("Unsupported RR given.")
    if record == "A":
        qtype = b'\x00\x01'
    if record == "AAAA":
        qtype = b'\x00\x1c'
    if record == "MX":
        qtype = b'\x00\x0f'
    if record == "PTR":
        qtype = b'\x00\x0c'
    if record == "PTR":
        # reverse IP is backward ip plus in-addr.arpa
        # so will be recreate the host to query and then make it in to bytes as
        # with the normal requests
        rev = host.split(".")
        rev.reverse()
        host = ""
        for quad in rev:
            host += quad + "."
        host += "in-addr.arpa"
    for label in host.split('.'):
        qname.extend(bytes([len(label)]))
        qname.extend(bytes(label, "utf-8"))

    # Finish the QNAME with 00
    qname.extend(bytes([0]))
    data = bytearray(qname)
    # print(data)

    data.extend(qtype)
    data.extend(qclass)
    # print("question", data)
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


def parse_label_format(label_bytes: bytearray) -> str:
    """
    Parses a 'label format' of bytes - like the opposite of what I make in 
    host_question()
    :param label_bytes: data to parse 
    :return: normal formatted string
    """
    result = ""
    start_char = 0
    while True:
        length = label_bytes[start_char]
        if label_bytes[start_char] == 00:
            result = result[:-1]
            break
        result += label_bytes[start_char + 1:length + start_char + 1].decode(
            "utf-8") + "."
        # print(data)

        start_char += length + 1

    return result


def parse_mx(rdata: bytearray):
    firstbyte = rdata[0:1]
    secondbyte = rdata[1:2]
    rest = rdata[2:]
    data = ""
    start_char = 0
    while True:
        length = rest[start_char]
        data += rest[start_char+1:length+start_char+1].decode("utf-8") + "."
        # print(data)
        start_char += length +1
        if not type(rest[start_char]):
            break
    # print(data)
    return data


def parse_mx_dnslib(response: bytearray) -> list:
    r = dnslib.DNSRecord.parse(response)
    mx_list = []
    for record in r.short().splitlines():
        mx_list.append(record.split(' ')[1])

    return mx_list


def parse_cname(response: bytearray):
    r = dnslib.DNSRecord.parse(response)
    for r in r.rr:
        if type(r.rdata) == dnslib.CNAME:
            return str(r.rdata)


def parse_reply(data: bytearray, q_bytes: bytearray) -> dict:
    """
    Takes DNS response and parses it
    :param data:
    :param q_bytes: the original domain/ip to lookup
    :param q_bytes: the question we sent so we have it as a reference
    :return:
    """
    bytes_array = bytearray(data)

    answer = dict()
    answer["id"] = bytes_array[0:2]
    flags = BitArray(bytes_array[2:4])
    answer_count: int = int.from_bytes(bytes_array[6:8], "big")
    start_of_answers = 12 + len(q_bytes)
    answers = bytes_array[start_of_answers:]
    # 11 or 00 in binary is the start the record
    byte_offset = 0
    list_mx_records = []
    list_a_records = []
    for ans in range(answer_count):
        this_answer = {}
        name = BitArray(answers[byte_offset+0:byte_offset+2])
        if name.bin.startswith("11"):
            pass
            # pointer = int.from_bytes(BitArray(name.bin[2:]).bytes, "big")

        # each answer consists of 10 bytes before the RDLENGTH
        ans_type = int.from_bytes(answers[byte_offset+2:byte_offset+4], "big")
        # this_answer["type"] = ans_type
        klass = int.from_bytes(answers[byte_offset+4:byte_offset+6], "big")

        rdlength = int.from_bytes(answers[byte_offset+10:byte_offset+12], "big")
        rdata = answers[byte_offset+12:byte_offset+12+rdlength]
        byte_offset = byte_offset + rdlength + 12
        if ans_type == 1:
            answer["ipv4"] = list_a_records
            list_a_records.append(parse_ipv4(rdata))
            # answer["ipv4"] = parse_ipv4(rdata)
        if ans_type == 5:
            answer["cname"] = parse_cname(data)
        if ans_type == 28:
            answer["ipv6"] = parse_ipv6(rdata)
        if ans_type == 15:
            list_mx_records = parse_mx_dnslib(data)
            answer["mx"] = list_mx_records
            break
        if ans_type == 12:
            answer["reverse"] = parse_label_format(rdata)

    return answer


def query_dns(dns: str, host: str, qtype: str="A") -> dict:
    """
    Queries the DNS server for the host given
    :param dns: string of ip
    :param host: string of address
    :param qtype: string of Question Type
    :return dict of data
    """
    answer = []
    dry_run = False
    address = (dns, 53)
    message, query = create_request_message(host, qtype)

    if not dry_run:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(message, address)

        data, _ = s.recvfrom(2048)
        # print("data:", data)
        answer = parse_reply(data, query)
    # print("answer", answer)
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
    # print(message.__len__())
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
    # print(message.__len__())
    # QDCOUNT
    if qd_count == 1:
        message.extend(b'\x00\x01')
    # ANCOUNT
    message.extend(b'\x00\x00')
    # NSCOUNT
    message.extend(b'\x00\x00')
    # ARCOUNT
    message.extend(b'\x00\x00')
    # print("header length:", message.__len__())
    # print(message)
    # Make the query
    query = host_question(host, qtype)
    message.extend(query)
    # print(message)
    # print("message length: ", message.__len__())
    return message, query


def runner(dns, host) -> CompleteResult:
    a = query_dns(dns, host, "A")
    aaaa = query_dns(dns, host, "AAAA")
    mx = query_dns(dns, host, "MX")

    result = {"host": host, **a, **aaaa, **mx}
    a = CompleteResult(result)
    return a


def cli_app():
    if len(sys.argv) < 3:
        dns = input("DNS Server IP Address?")
        host = input("Server to query?")
    else:
        dns, host = sys.argv[1], sys.argv[2]

    result = runner(dns, host)
    # print(f"Host: {host}")
    # if "ipv4" in result:
    #     print(f"IPv4: {result.get('ipv4','None')}")
    # if "ipv6" in result:
    #     print(f"IPv6: {result.get('ipv6','None')}")
    # if "reverse" in result:
    #     print(f"Name: {result.get('reverse','None')}")
    print(result)


if __name__ == '__main__':
    cli_app()