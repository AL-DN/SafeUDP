import random
import hashlib
import sys

# We understand that creating packet data on creation will lead to inconsistent packet
# data on event of resend

# Stop and Wait: This can be solved by saving the previous packet sent just incase it needs to be resent
# on ACK it then updates it to packet currently being sent

# GoBackN: Create a list of packets in window so that in case of resend it will
# resend packets with same data

# Params:
    # packet_num: the sequence number 
    # data = generated on creation of packet consists of original data and corresponding has value
    # bit_error = marking True will induce bit errors at the specified ( 0.02 ) prob

class Packet:

    def __init__(self, packet_num):
        self.packet_num = packet_num
        self.data = self.createRandomData()

        

################################################################################################

    def createRandomData(self)-> str:

        ################ CREATES ORG DATA #############################

        # 1KB Packet =  125 Bytes - 32(HASH) = 93 Bytes for data
        dList = []
        for i in range(93):
            newInt = random.randint(0,9)
            dList.append(newInt)

        unHashedStrData = ''.join(str(i) for i in dList)

        ################ CREATES HASH VALUE #############################

        unHashedByteData = unHashedStrData.encode()        # hashValue be used to detect bit errors
        # 256 bit hash algorith SHA-256 (suprised by power of alg)
        # 64 char long str (2 hex chars -> 1 byte) -> (32 bytes) 
        hashValue = hashlib.sha256(unHashedByteData).hexdigest()
        
        return unHashedStrData + "|" + hashValue
    
################################################################################################

    