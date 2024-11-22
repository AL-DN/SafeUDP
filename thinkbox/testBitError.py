
num = 12
bNum = bin(num)
#removes data type
print(bNum)
bNum = bNum[2:]
print(bNum)
bList = list(bNum)
print(bList)
# incrments or decrements number by 1
bList[len(bList)-1] = '1' if bList[len(bList)-1] == '0' else '0'
print(''.join(bList))
print(int(''.join(bList)))
newPacketNum = int(''.join(bList), 2)

print(newPacketNum)