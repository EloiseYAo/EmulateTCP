# EmulateTCP

#### Files Description

##### 1. sender.py

This is the TCP data sender, which sends the data file. It is highly recommended to run first. 

(Because if you run the receiver first, the receiver will send request to the sedner for the data, however, the sender can't get the request cuz it is not open, so you need to wait for the receiver timeout and resend the request)

##### 2. receiver.py

This is the TCP data receiver, which sends the request for the data file and receiver the data.

##### 3. segment.py

It is used to make the segment, which can assemble header, and encapsulate the header and data. It also has a function to check checksum.



#### Running Commands

In order to run the program,  following commands need to be inputed separately in three terminal windows, for the link emulator, sender and receiver respectively:

##### 1. Link Emulator:

​	- newudpl -vv -i 127.0.0.1/41194 -o 127.0.0.1/41191 [FLAGS]

​	FLAGS: I used the flags -L7 -B20 -O9 -d0.2, I recommend using the flags, cuz the file is a little bit large, the more delay, the more time to finish the transmission.

​	The link I established:

​	localhost(127.0.0.1)/41194 ->

​			wujinyaodeMBP(192.168.1.185)/41192/41193 ->

​			localhost(127.0.0.1)/41191

​	Note: In the sender and receiver sockets, the host is hardcode as 

​			sednerSocket.bind(('127.0.0.1', ack_port_number))

​			revSocket.bind(('127.0.0.1', listening_port))

​	so, please use the localhost(127.0.0.1) as the source host and destination host

##### 2. Sender:

​	- python sender.py [send_file] [address_of_udpl] [port_number_of_udpl] [window_size] [ack_port_number]

​	the command I used:

​	- python sender.py send_file.txt 192.168.1.185 41192 5 41194

##### 3. Receiver:

​	- python receiver.py [write_file] [listening_port] [address_for_acks] [port_for_acks]

​	the command I used:

​	- python receiver.py write_file.txt 41191 127.0.0.1 41194



#### Bugs and Features

1.Because both corrupted packets and out of order packets are directly thrown away and wait for retransmission, a large number of packets will be thrown away, which will lead to a lot of traffic in traffic, but a lot of traffic will be wasted

2.From now, I didn't find any bug if you correctly use localhost as the source host and destination host. I don't try the program on any other machine, just on my own laptop, so I'm not sure if it will report something wrong when you run it on different machines. But I think if you just run on your laptop and use the localhost, everything will be fine. So please follow the above running commands.
