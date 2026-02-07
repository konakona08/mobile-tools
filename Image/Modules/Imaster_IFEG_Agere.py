from __future__ import print_function
from unicorn import *
from unicorn.arm_const import *
from . import flashParser
import gc
import io
import typing
import struct
from PIL import Image
import os

ARM_RTS_LONG = b"\x1E\xFF\x2F\xE1"
ARM_RTS = b"\x70\x47"

IFG_DIFF_TABLE_ADDRESS = 0x0100ead0

#MEMCPY_ADDRESS = [0x1cacca, 0x2909f4]
#MALLOC_ADDRESS = [0x1cacb8, 0x290a0c]
#FREE_ADDRESS = [0x1cacbe, 0x290a00]

MEMCPY_ADDRESS = [0x2909f4]
MALLOC_ADDRESS = [0x290a0c]
FREE_ADDRESS = [0x290a00]

MALLOC_BUFFER_ADDRESS = 0x08000000
MALLOC_USED = 0
MALLOC_MAP = {}

def hook_code(uc, address, size, _):    
    #print(hex(address), 4, uc.mem_read(address, size))
    if address in MEMCPY_ADDRESS: # Memcpy            
        dest, src, length = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1), uc.reg_read(UC_ARM_REG_R2)   
        #print("memcpy", hex(dest), hex(src), hex(length)) 
        uc.mem_write(dest, bytes(uc.mem_read(src, length)))      

    elif address in MALLOC_ADDRESS: # Malloc
        size = uc.reg_read(UC_ARM_REG_R0)
        uc.reg_set(UC_ARM_REG_R0, MALLOC_BUFFER_ADDRESS+MALLOC_USED)
        MALLOC_MAP[MALLOC_BUFFER_ADDRESS+MALLOC_USED] = size
        MALLOC_USED += size        
        
    elif address in FREE_ADDRESS: # Free    
        ptr = uc.reg_read(UC_ARM_REG_R0)

        #uc.mem_write(ptr, b"\0\0\0\0")            
    #print(uc.mem_read(address, size))
    #print(hex(uc.reg_read(UC_ARM_REG_LR)))

def vDecodeFrame(data, length):
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)

    mu.mem_map(0x0, 4*1024*1024) # Code
    mu.mem_map(0x01000000, 16*1024*1024) # Code Ram
    mu.mem_map(0x02000000, 16*1024*1024) # Buffer
    mu.mem_map(0x03000000, 16*1024*1024) # Stack Pointer
    mu.mem_map(MALLOC_BUFFER_ADDRESS, 1*1024*1024) # Malloc buffer

    mu.ctl_exits_enabled(True)
    mu.ctl_set_exits([0x0])

    flashParser.parse(mu, os.path.join(os.path.dirname(__file__), "agereC140.fls"))

    mu.mem_write(0x02000000, data)
    
    out_offset = 0x02000000 + len(data) + 0x10000

    mu.reg_write(UC_ARM_REG_R0, 0x02000000)        
    mu.reg_write(UC_ARM_REG_R1, out_offset)

    mu.reg_write(UC_ARM_REG_SP, 0x03040000)        

    mu.reg_write(UC_ARM_REG_APSR, 0xffffffff)
    mu.hook_add(UC_HOOK_CODE, hook_code)
    
    for f in MEMCPY_ADDRESS+MALLOC_ADDRESS+FREE_ADDRESS:
        mu.mem_write(f, ARM_RTS_LONG)

    mu.emu_start(0x26460c, 0x28000)
    
    temp = mu.mem_read(out_offset, length)    
    
    del mu
    gc.collect()

    return temp

def ifgDecode(file: typing.Union[io.RawIOBase, bytearray, bytes, str]):
    dataIn = None
    if isinstance(file, bytes) or isinstance(file, bytearray):
        dataIn = file
    elif isinstance(file, io.RawIOBase):
        dataIn = file.read()
    else:
        dataIn = open(file, "rb").read()

    header = dataIn[:0x18]
    assert header[:0x4] == b"IFEG", "Not a valid IFG file."
    assert header[0xb] == 0x56, "Not an Agere IFG file."
    assert header[0x9] in [0, 1], "Invalid codec type."

    width, height = struct.unpack("<HH", dataIn[4:8])
    data = vDecodeFrame(dataIn, (width*height*2))

    return Image.frombytes("RGB", (width, height), data, "raw", "BGR;16", 0, 1)