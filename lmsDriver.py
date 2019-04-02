#LMS Driver

#Dependencies
import ubmsLoad
import struct

#Create load
load1 = ubmsLoad.uLoad(0,6,0,0.200,10)

#Print all values
for i in vars(load1):
    print(vars(load1)[i])

#Pack values into struct
packed = struct.pack('9f', *(vars(load1).values()))
#Print packed values
print(packed)
#Unpack values
unpacked = struct.unpack('9f',packed)
#Print unpacked values
print(unpacked)

