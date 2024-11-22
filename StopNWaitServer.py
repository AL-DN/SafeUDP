# Author: Alden Sahi
# Server for Stop and Wait Protocol


import socket
import time
import random
import hashlib

SERVER_ADDRESS_PORT = ("127.0.0.1", 20001)
BUFFER_SIZE = 4096
TIMEOUT_DURATION = 1
PL_PROB = 0.002

def doesPacketLossOccur() -> bool: 
    return random.random() < PL_PROB

packets_received = 0

with open('SNW_S.txt', 'w') as file:
    
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
            print(f"Packet {packets_received+1} received correctly\n",file=file)
            response = "ACK"
            packets_received += 1
        else:
            print(f"Packet {packets_received+1} was corrupted\n",file=file)
            response = "NAK"
    
        
        UDPServerSocket.sendto(response.encode(), client_address)

########################## FINISHING #########################################

    print('DONE!')
    UDPServerSocket.close()
    print("Server received all {} packets. Stopping.".format(packets_received),file=file)