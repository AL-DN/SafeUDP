# GOAL: How to find start of window relative to packet number
    # Given: 
        # p: packet number
        # w: window size
import math

p = 215
w = 100
print(p//w)
print(p//w)
print(math.ceil(p/w))

# LEARNED: Pythons Division operation alwasy does floor division