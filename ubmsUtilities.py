#Utility functions for uBMS

#Dependencies
import struct

#Convert class object into packed struct
def objToStruct(obj):
    
    #Determine number of values in object
    N = len(vars(obj))

    #Create data var to store values
    data = vars(obj).values()

    #Package values
    pkg = struct.pack('f'*N, *data)
    size = len(pkg)

    #Return package and value count
    return pkg, N, size

#Convert packaged data into original object
def structToObj(pkg,N):

    #Unpackage the struct
    obj = struct.unpack('f'*N,pkg)

    #Return object
    return obj
