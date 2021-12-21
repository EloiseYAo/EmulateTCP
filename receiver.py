from socket import *
import segment, time, sys
import socket as s

# file listening_port address_for_acks port_for_acks
# receiver's parameter
# write_file='write_file.txt'
# listening_port = 41191
# address_for_acks = '127.0.0.1'
# port_for_acks = 41194

try:
    write_file = sys.argv[1]
    listening_port = int(sys.argv[2])
    address_for_acks = sys.argv[3]
    port_for_acks = int(sys.argv[4])
except (ValueError, TypeError) as e:
    print(e)
    exit("Please type: $ receiver.py [write_file] [listening_port] [address_for_acks] [port_for_acks]")

ack_address = (address_for_acks, port_for_acks)

# some global values
seq_c = 0 # the sequence number of receiver
ack_c = 0 # the ack from sender
last_rev_seq_s = -1
fin = 0
window_size = 0
# global timeout_value, rtt_deviation, estimated_RTT
timeout_value = 10
rtt_deviation = 0
estimated_RTT = 0.5

# create the receiver socket
revSocket = socket(AF_INET, SOCK_DGRAM)
revSocket.bind(('127.0.0.1', listening_port))

# start connection
# cuz the first packet to open the transmission doesn't need the ack
# so just send a meaningless number 100(it can be changed as any other number)
start_segmeng = segment.make_segment(seq_c,100, ''.encode(),0, 0)
revSocket.sendto(start_segmeng, ack_address)
seq_c +=1
send_time = time.time()


while True:
    try:
        # set timeout value
        revSocket.settimeout(timeout_value)
        message, senderAddress = revSocket.recvfrom(576)
        print("From Sender: ",senderAddress)

        # calculate the TimeoutInterval
        rev_time = time.time()
        sampleRTT = rev_time - send_time
        estimated_RTT = estimated_RTT * (0.875) + sampleRTT * (0.125)
        rtt_deviation = 0.75 * (rtt_deviation) + 0.25 * abs(sampleRTT - estimated_RTT)
        timeout_value = estimated_RTT + 4 * rtt_deviation

        # unpack the segement to get the TCP header values and data
        seq_s, ack_s, fin, window_size, checksum, data = segment.unpack_segment(message)
        # print("seq_c:", seq_c)
        # print("ack_c:", ack_c)
        print("last rev seq:", last_rev_seq_s)
        print("seq_s:", seq_s)
        print("ack_s:", ack_s)

        # use the checksum to check if the packet is corrupted
        if (str(checksum).rstrip(' \t\r\n\0') == str(segment.check_sum(seq_s, ack_s, data, fin, window_size)).rstrip(' \t\r\n\0')):

            # check if the seq# from the sender is the next segment seq# that the receiver needs
            if (seq_s == last_rev_seq_s + 1):
                # check if the segment is the last one
                if fin == 0:
                    ack_c = seq_s + 1
                    c_segment = segment.make_segment(seq_c, ack_c, ''.encode(), 0, window_size)
                    revSocket.sendto(c_segment, ack_address)
                    send_time = time.time()
                    seq_c += 1
                    last_rev_seq_s = seq_s
                    # write the data to the file
                    new_fo = open(write_file, 'a')
                    new_fo.write(data.decode())
                    new_fo.close()
                else:
                    ack_c = seq_s + 1
                    c_segment = segment.make_segment(seq_c, ack_c, ''.encode(), 1, window_size)
                    revSocket.sendto(c_segment, ack_address)
                    last_rev_seq_s = seq_s
                    # if it is the last one, it only need to write the data to the file
                    new_fo = open(write_file, 'a')
                    new_fo.write(data.decode())
                    new_fo.close()
                    break
            else:
                print("Not match! Drop it!")
        else:
            print("Corrupted packet! Drop it!")
    except s.timeout:
        # resend
        print("Timeout! Resend!")
        if seq_c != 0 :
            seq_c -= 1
        c_segment = segment.make_segment(seq_c, ack_c, ''.encode(), fin, window_size)
        revSocket.sendto(c_segment, ack_address)
        send_time = time.time()
        seq_c += 1

print()
print("Final packet has been received! Close receiver socket.")
print("The total number of packets:",last_rev_seq_s)
print()
revSocket.close()

