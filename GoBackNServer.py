# Author: Alden Sahi
# Server for Go Back N Protocol

import socket
import time
import hashlib
import random
from packet import Packet

SERVER_ADDRESS_PORT = ("127.0.0.1", 20002)
BUFFER_SIZE = 1024
TIMEOUT_DURATION = 1
WINDOW_SIZE = 100
PL_PROB = 0.002

################### METHODS #######################################

def doesPacketLossOccur() -> bool: 
    return random.random() < PL_PROB

####################################################################

bResponse = 'ACK'
packets_received = 0

with open('GBN_S.txt', 'w') as file:

    #starts server
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind(SERVER_ADDRESS_PORT)
    print("UDP server up and listening",file=file)

    # ensures server will continue to run until 1000 packets are recieved
    while packets_received < 1000:

        # PROGRESS BAR
        if packets_received % 100 == 0:
            print(f'Progress: {(packets_received/1000)*100} %')

        # PACKET LOSS
        if doesPacketLossOccur():
            print(f"Packet Loss Occured!\n",file=file)

            # Pretends not to recieve Packet
            UDPServerSocket.sendto('NAK'.encode(), client_address)
            continue

########################### PROCESSING PACKET ###################################

        # recieves packet data
        data, client_address = UDPServerSocket.recvfrom(BUFFER_SIZE)
        print(f"Raw Data Received (bytes): {data}", file=file)

        # decodes b-str back to str and removes whitespace if any
        receivedData = data.decode().strip()
        print(f"Decoded Data (after strip): '{receivedData}'", file=file)

        #splits data into pData and recievedHash
        pData, receivedHash = receivedData.split("|")
        print(f"Data Part: '{pData}', Received Hash: '{receivedHash}'", file=file)

        
        # Recalculate Hash
        calculatedHash = hashlib.sha256(pData.encode()).hexdigest()
        print(f"Calculated Hash: {calculatedHash}", file=file)
        
        time.sleep(0.025)

########################### SENDING RESPONSE ###################################


        print("Expected Hash:", receivedHash ,file=file)
        print("Calculated Hash:", calculatedHash ,file=file)
        if receivedHash == calculatedHash:
            print(f'Packet Number {packets_received} was ACK',file=file)
            pResponse = "ACK"
        else:
            print(f'Packet Number {packets_received} was NAK',file=file)
            pResponse = "NAK"
        
        packets_received += 1

        # if we recieve a single NAK the whole block is corrupted
        if pResponse == "NAK":
            bResponse = "NAK"
            print(f'\n BLOCK RESPONSE UPDATED TO {bResponse} \n',file=file)
            

        print(f"Response from Block: {bResponse}",file=file)
        print(f'Total Packets Recieved: {packets_received}',file=file)

        # After entire block is processed and block response in NAK
        if packets_received % WINDOW_SIZE == 0 and bResponse == "NAK":

            # Sends NAK to Client
            print(f"Server Sending {bResponse.encode()} {client_address}",file=file)
            UDPServerSocket.sendto(bResponse.encode(), client_address)

            #Resets Block Response
            bResponse = "ACK"

            # Resends Block of Packets
            packets_received = (packets_received - WINDOW_SIZE)

        # After entire block is processed and block response in ACK
        elif packets_received % WINDOW_SIZE == 0 and bResponse == "ACK":

            # Sends ACK to Client
            UDPServerSocket.sendto(bResponse.encode(), client_address)


########################## FINISHING #########################################

    print('DONE!')
    UDPServerSocket.close()
    print("Server received all {} packets. Stopping.".format(packets_received),file=file)