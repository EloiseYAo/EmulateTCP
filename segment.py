import struct


data_size = 556 #bytes
header_format = "IIIII"

content_data = ''
content_data = content_data.encode()


def make_segment(seq_num, ack_num, data, fin, window_size):
    # calculate the checksum to find the corrupted segment
    checksum = check_sum(seq_num,ack_num,data,fin,window_size)
    # pack the TCP header, whose size is 5*4 = 20 bytes
    header = struct.pack(header_format,seq_num,ack_num,fin,window_size,checksum)
    # make the segment
    segment = header + data
    return segment


def unpack_segment(segment):
    # get the TCP header
    header = segment[:20]
    seq_number, ack_number, fin, window_size, checksum = struct.unpack(header_format,header)
    # get the data
    data = segment[20:]
    return seq_number, ack_number, fin, window_size, checksum,data


# calculate the checksum
def check_sum(seq_num, ack_num, data, fin, window_size):
    total_segment = str(seq_num)+str(ack_num)+str(fin)+str(fin)+str(window_size)+str(data)
    nleft = len(total_segment)
    sum = 0
    pos = 0
    while nleft > 1:
        sum = ord(total_segment[pos]) * 256 + (ord(total_segment[pos + 1]) + sum)
        pos = pos + 2
        nleft = nleft - 2
    if nleft == 1:
        sum = sum + ord(total_segment[pos]) * 256

    sum = (sum >> 16) + (sum & 0xFFFF)
    sum += (sum >> 16)
    sum = (~sum & 0xFFFF)
    return sum




