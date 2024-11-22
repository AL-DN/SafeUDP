# Author: Alden Sahi
# Client for Go Back N Protocol

import socket
import time
import select
import random
import copy
from packet import Packet


SERVER_ADDRESS_PORT = ("127.0.0.1", 20002)
BUFFER_SIZE = 1000
TIMEOUT_DURATION = 1
WINDOW_SIZE = 100

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

count = 1
nakFlag = 0
cachedPacketList = [Packet] * WINDOW_SIZE

# client socket setup on (family)IPV4 and (type)UDP
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# starts runtime
start_time = time.time()
with open('GBN_C.txt', 'w') as file:

    #cant use for-loop because we need a way to resend packets multiple times
    # counts number of packets
    while count<=1000:  

        # 25ms wait on client side to simulate 50ms RTT
        time.sleep(0.025) 

        ################# SENDING PACKETS #########################################

        if nakFlag:

            print("Sending Cached Packet Block!", file=file)

            # Get Packet from Buffer
            packetToSend = cachedPacketList[(count % WINDOW_SIZE)-1]

            # Bit Error 
            packetToSend = createBitError(packetToSend)

            # Sends encoded packet data
            UDPClientSocket.sendto(packetToSend.data.encode(), SERVER_ADDRESS_PORT)
            print("Packet Number: ", packetToSend.packet_num, file=file)
            print("Sending Packet Data: ", packetToSend.data, file=file)

        else:

            # Creates Packet 
            packetToCache = Packet(packet_num=count)

            # Caches Packet 
            cachedPacketList[(count % WINDOW_SIZE)-1] = packetToCache

            # Bit Error 
            packetToSend = createBitError(packetToCache)

            # Sends encoded packet data
            UDPClientSocket.sendto(packetToSend.data.encode(), SERVER_ADDRESS_PORT)
            print("Packet Number: ", packetToSend.packet_num, file=file)
            print("Sending Packet Data: ", packetToSend.data, file=file)

       

    ########################## RECIEVING RESPONSE ####################################

        # GoBackN only checks for validation after packet block
        if count % WINDOW_SIZE == 0:
            while True: 
                #waits for event to occur on UDPClientSocket within timeout duration
                check = select.select([UDPClientSocket], [], [],TIMEOUT_DURATION)
                # if there is readable message before timeout 
                if check[0]:
                    bResp, _ = UDPClientSocket.recvfrom(BUFFER_SIZE)
                    print(f'Response from Block was {bResp.decode()} \n\n', file=file)
                    if bResp.decode() == "ACK":
                        nakFlag = 0
                        # Received ACK, proceed to the next packet
                        # packet_num += 1
                        break
                    elif bResp.decode() == "NAK":
                        nakFlag = 1
                        # Received NAK, send back to start of block
                        # since we will only reach this code at end of block 
                        # operation is easy
                        count = count - WINDOW_SIZE
                        print(f"NAK Recieved, Restarting at {count} \n\n", file=file)
                        break
                else:
                    # Packet Loss occured, retransmit the same packet
                    print("TimedOut: Resending Packet", file=file)
                    # since incrmement of packet num happens every iteration 
                    # we want to revert its effects thus resending same packet
                    count -= 1
                    break

        count += 1


    # Runtime Results
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Elapsed time:", elapsed_time, "seconds", file=file)