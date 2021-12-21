from socket import *
import sys, segment, time
import socket as s



# send_file = "send_file.txt"
# address_of_udpl = '192.168.1.185'
# port_number_of_udpl = 41192
# WS = 5 # window size
# ack_port_number= 41194

# some global values
max_data_size = 556
max_seg_size = 576
seq_s = 0 # the sequence# of sender
ack_s = 0 # the ack# from receiver
fin_s = 0 # the FIN flage
res_data = ''.encode()  # the data will be sent
# global timeout_value, rtt_deviation, estimated_RTT
timeout_value = 10
rtt_deviation = 0
estimated_RTT = 0.5

# tcpclient file address_of_udpl port_number_of_udpl windowsize ack_port_number
# sender's parameter
try:
    send_file = sys.argv[1]
    address_of_udpl = sys.argv[2]
    port_number_of_udpl = int(sys.argv[3])
    WS = int(sys.argv[4]) # window size
    ack_port_number= int(sys.argv[5])
    check_WS = WS % max_seg_size
except (ValueError,TypeError) as e:
    print(e)
    exit("Please type: $ sender.py [send_file] [address_of_udpl] [port_number_of_udpl] [window_size] [ack_port_number]")

# check if the input of window size is mutiple of 576
if check_WS != 0:
    raise Exception('Window size must be mutiple of 576 bytes!')
    sys.exit()

rev_address = (address_of_udpl,port_number_of_udpl)


send_buffer = {} # {seq_s: segment} -- save the packets have not receive the ACK
duplicate_ack = {} # {ack_c: number of times} -- save the number of times of each ack, when first time, the value is 0

# create sender socket
sednerSocket = socket(AF_INET, SOCK_DGRAM)
sednerSocket.bind(('127.0.0.1', ack_port_number))

# open file
try:
    send_fo = open(send_file, 'br')
except IOError:
    print(send_file + " was not found.")
    sednerSocket.close()
    sys.exit()

# get file content for sending ( at most 556 bytes very time)
def make_data():
    content_data = send_fo.read(max_data_size)
    len_data = len(content_data)
    return content_data, len_data


while True:
    try:
        if seq_s>0:
            # calculate the TimeoutInterval
            rev_time = time.time()
            sampleRTT = rev_time - send_time
            estimated_RTT = estimated_RTT * (0.875) + sampleRTT * (0.125)
            rtt_deviation = 0.75 * (rtt_deviation) + 0.25 * abs(sampleRTT - estimated_RTT)
            timeout_value = estimated_RTT + 4 * rtt_deviation

        #set timeout value
        sednerSocket.settimeout(timeout_value)
        message, revAddress = sednerSocket.recvfrom(576)
        print("From Receiver: ",revAddress)

        # unpack the segement to get the TCP header values and data
        seq_c, ack_c, fin_s , window_size, checksum, data = segment.unpack_segment(message)

        # print("seq_s:", seq_s)
        # print("ack_s:", ack_s)
        print("seq_c:", seq_c)
        print("ack_c:", ack_c)

        # use the checksum to check if the packet is corrupted
        if (str(checksum).rstrip(' \t\r\n\0') == str(segment.check_sum(seq_c, ack_c, data, fin_s, window_size)).rstrip(
                ' \t\r\n\0')):
            # delete the segment in buffer, which has been received by the receiver
            if (ack_c - 1) in send_buffer:
                print("del seq",(ack_c-1),"in buffer")
                del send_buffer[ack_c - 1]

            # if it is the first packet, the window_size in header from the receiver is 0
            # we need to reset it as our input
            if window_size == 0:
                window_size = WS

            # if the FIN is 1, and all packets have been received (the send_buffer is empty), close the socket
            if fin_s == 1 and len(send_buffer) == 0:
                print()
                print("Final packet has been received! Close sender socket.")
                print()
                sednerSocket.close()
                break

            # after receiving the ack, there are 3 more acks have been received, resend it immediately
            if ack_c in duplicate_ack:
                duplicate_ack[ack_c] += 1
                if duplicate_ack[ack_c] >= 3:
                    print("duplicate for 3 times! resend!")
                    # print(send_buffer)
                    for v in send_buffer.values():
                        sednerSocket.sendto(v, rev_address)
                    send_time = time.time()
                    duplicate_ack[ack_c] = 0
            else:
                duplicate_ack[ack_c] = 0

            # send segments
            if seq_c == 0:
                if ack_c == 1:
                    ack_s = 1
                if ack_c ==0:
                    seq_s = 0
                # use seq, ack, data and FIN to make the segments
                send_segment = segment.make_segment(seq_s,ack_s,''.encode(),fin_s,window_size)
                sednerSocket.sendto(send_segment, rev_address)
                send_time = time.time()
                seq_s = 1
            else:
                # check if the ack# from the receiver matches with the seq# of sender
                ack_s = seq_c + 1
                free_size = int(window_size/max_seg_size) - (seq_s - ack_c)
                if( free_size > 0 ):
                    for i in range(free_size):
                        # get the content data for sending
                        res_data, len_data = make_data()
                        # if the length of data, the segment is not the last one
                        if len_data == max_data_size:
                            send_segment = segment.make_segment(seq_s, ack_s, res_data, fin_s, window_size)
                            send_buffer[seq_s] = send_segment
                            sednerSocket.sendto(send_segment, rev_address)
                            # send_time = time.time()
                            seq_s += 1
                        # otherwise it is the last one, need to set FIN to 1
                        else:
                            if len_data != 0:
                                fin_s = 1
                                send_segment = segment.make_segment(seq_s, ack_s, res_data, fin_s, window_size)
                                send_buffer[seq_s] = send_segment
                                sednerSocket.sendto(send_segment, rev_address)
                                # send_time = time.time()
                                seq_s += 1
                        if i == 0:
                            send_time = time.time()

        else:
            print("Corrupted packet! Drop it!")
    except s.timeout:
        print("Timeout! Resend!")
        # resend the packets in the buffer
        # print(send_buffer)
        for v in send_buffer.values():
            sednerSocket.sendto(v, rev_address)
        send_time = time.time()









