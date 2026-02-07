from unicorn import *
from unicorn.arm_const import *
import struct

def parse(mu: Uc, file: str):
    flash = open(file, "rb")
    assert flash.read(2) == b"FL"
    count = struct.unpack("<L", flash.read(4))[0]
    for _ in range(count):
        offset, size = struct.unpack("<LL", flash.read(8))        
        data = flash.read(size)        
        mu.mem_write(offset, data)