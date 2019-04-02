import struct
import ubmsLoad
import json

a = ubmsLoad.uLoad(0,6,0,0.200,10,100)
s = list(vars(a).values())
s = str(s)
s = bytes(s, 'utf-8')    # Or other appropriate encoding
data = struct.pack("I", len(s)) + s

print(data)

#Time to unpack!
(i,), data = struct.unpack("I", data[:4]), data[4:]
s, data = data[:i], data[i:]

print(s)
print(data)
