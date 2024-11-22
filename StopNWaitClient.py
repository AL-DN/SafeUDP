# Author: Alden Sahi
# Client for Stop and Wait Protocol

import socket
import time
import select
import random
import copy
from packet import Packet

SERVER_ADDRESS_PORT = ("127.0.0.1", 20001)
BUFFER_SIZE = 4096
TIMEOUT_DURATION = 1

################### METHODS #######################################


def createBitError(packet: Packet) -> Packet:

    # Params: Packet
    # Output: New Packet with same hash value but different data

    # This achieves theory because when packet gets to the server
    # the server will recompute hash of data sent vs the one couple with data
    # these two hashes will be different because we altered orginal data that was used

    tempPacket = copy.deepcopy(packet)

    
    #print(f'Original Data {packet.data} \n')
    if random.random() < 0.002:
        #print("Inducing Bit Error",file='SNW_C.txt')
        splitData = tempPacket.data.split('|')
        #print(f'Data After split {splitData} \n')
        # Extract the data portion (before the "|")
        bNum = bin(int(splitData[0]))

        #removes binary prefix '0b'
        bNum = bNum[2:]

        #make bin str mutable
        bList = list(bNum)
        
        #generates random index within indicies 
        randIndex = random.randint(0,len(bList)-1)

        # flips bit at random index
        bList[randIndex] = '1' if bList[randIndex] == '0' else '0'

        # Convert the binary list back to a string of bits
        bitErrorData = str(int(''.join(bList), 2))
        #print(f'Data Trying to Inject: {bitErrorData} \n')

        #print(f'List Before to Inject: {splitData} \n')
        #inject bit error data into packet
        splitData[0] = bitErrorData

        #print(f'List After to Inject: {splitData} \n')
        
        #seal it back up
        tempPacket.data =  '|'.join(splitData)
        return tempPacket

    # Return
    tempPacket.data = packet.data
    return tempPacket

####################################################################

# Global Variables
count = 1
cachedPacket: Packet 
nakFlag = 0  


# client socket setup on (family)IPV4 and (type)UDP
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# starts runtime
start_time = time.time()

# cant use for-loop because we need a way to resend packets multiple times
# counts number of packets

with open('SNW_C.txt', 'w') as file:

    while count<=1000:
        
        # 25ms wait on client side to simulate 50ms RTT
        time.sleep(0.025)

        # CACHING LOGIC

        if nakFlag:

            print("Sending Cached Packet!", file=file)

            # Bit Error 
            packetToSend = createBitError(cachedPacket)

            # Sends encoded packet data
            UDPClientSocket.sendto(packetToSend.data.encode(), SERVER_ADDRESS_PORT)
            print("Packet Number: ", packetToSend.packet_num, file=file)
            print("Sending Packet Data: ", packetToSend.data, file=file)

        else:

            # Creates Packet 
            cachedPacket = Packet(packet_num=count)

            # Bit Error 
            packetToSend = createBitError(cachedPacket)

            # Sends encoded packet data
            UDPClientSocket.sendto(packetToSend.data.encode(), SERVER_ADDRESS_PORT)
            print("Packet Number: ", packetToSend.packet_num, file=file)
            print("Sending Packet Data: ", packetToSend.data, file=file)
            

       

    ########################## RECIEVING RESPONSE ####################################


        while True: 
            # Waits for ACK, NAK or TIMEOUT
            check = select.select([UDPClientSocket], [], [], TIMEOUT_DURATION)

            # If response occurs
            if check[0]:

                # Extract Response
                resp, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)

                # Determines if Packet was sent correctly
                if resp.decode() == "ACK":
                    # Received ACK, proceed to the next packet
                    print(f'Packet Number {count} was ACK\n', file=file)
                    nakFlag = 0 
                    count += 1
                    break

                elif resp.decode() == "NAK":
                    print(f'Packet Number {count} was NAK\n', file=file)
                    nakFlag = 1
                    # Received NAK, retransmit the same packet
                    break

            else:
                # Packet Loss occured, retransmit the same packet (TODO: Save Old Packet!
                print("TimeOut: Resending....",file=file)
                break

    
    # Runtime Results
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed time:", elapsed_time, "seconds",file=file)