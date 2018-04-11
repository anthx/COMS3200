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

def query_dns(dns: str, host: str) -> dict:
    """
    Queries the DNS server for the host given
    :param dns: string of ip
    :param host: string on address
    :return: dict of data
    """

    address = (dns, 53)
    qr = 0
    op_code: int = 0
    tc = 0
    rd = 1
    qd_count = 1
    message = bytearray(b'\xAC\xAC')

    flags = BitArray("0b"+
                     format(qr, 'b')+
                     format(op_code,'04b')+
                     format(0, 'b')+
                     format(tc, 'b')+
                     format(rd, 'b')+
                     format(qd_count, 'b')+
                     format(0, 'b')+
                     format(0, 'b')+
                     format(0))
    print(flags.bin)
    message.append(flags.int)
    print(message)
    # Make the query



    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(address)

    answer = {"ipv4": "0.0.0.0"}
    return answer

query_dns("", "")