from __future__ import print_function
from unicorn import *
from unicorn.arm_const import *
from . import flashParser
import gc
import os
import io
import typing
import struct
from . import ucHeapLib
from PIL import Image

ARM_RTS_LONG = b"\x1E\xFF\x2F\xE1"
ARM_RTS = b"\x70\x47"

#MEMCPY_ADDRESS = [0x1cacca, 0x2909f4]
#MALLOC_ADDRESS = [0x1cacb8, 0x290a0c]
#FREE_ADDRESS = [0x1cacbe, 0x290a00]

MEMCPY_ADDRESS = [0xa049c, 0x854dc]
MALLOC_ADDRESS = [0xa0490, 0x854ca]
FREE_ADDRESS = [0xa047c, 0x854be]
MEMSET_ADDRESS = [0xa04a4]

MALLOC_BUFFER_ADDRESS = 0x08000000
MALLOC_USED = 0
MALLOC_MAP = {}
FLASH = os.path.join(os.path.dirname(__file__), "swiftE1150.fls")

def hook_code(uc: Uc, address, size, heap):
    global MALLOC_USED, MALLOC_MAP    
    #print(hex(address), 4, uc.mem_read(address, size))
    if address in MEMCPY_ADDRESS: # Memcpy            
        dest, src, length = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1), uc.reg_read(UC_ARM_REG_R2)       
        uc.mem_write(dest, bytes(uc.mem_read(src, length)))      

    elif address in MALLOC_ADDRESS: # Malloc
        size = uc.reg_read(UC_ARM_REG_R0)
        uc.reg_write(UC_ARM_REG_R0, heap.malloc(size))
        #print("malloc",hex(size))
        #uc.reg_write(UC_ARM_REG_R0, heap.malloc(size))        
        #print("returns",hex(uc.reg_read(UC_ARM_REG_R0)))
        
    elif address in MEMSET_ADDRESS: # Memset
        dest, data, count = uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1), uc.reg_read(UC_ARM_REG_R2)   
        for _ in range(count):
            uc.mem_write(dest, bytes([data]))
    
    elif address in FREE_ADDRESS: # Free    
        ptr = uc.reg_read(UC_ARM_REG_R0)        
        heap.free(ptr)
        #print("free",hex(ptr))
        #heap.free(ptr)
        #uc.reg_write(UC_ARM_REG_R0, heap.malloc(size))        
        #print("returns",uc.reg_read(UC_ARM_REG_R0))

        #uc.mem_write(ptr, b"\0\0\0\0")            
    #print(uc.mem_read(address, size))
    #print(hex(uc.reg_read(UC_ARM_REG_LR)))

def vDecodeFrame(data, length):
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    heap = ucHeapLib.UnicornSimpleHeap(mu)

    mu.mem_map(0x0, 4*1024*1024) # Code
    mu.mem_map(0xa8000000, 16*1024*1024) # Code Ram
    mu.mem_map(0x02000000, 16*1024*1024) # Buffer
    mu.mem_map(0x03000000, 16*1024*1024) # Stack Pointer
    #mu.mem_map(MALLOC_BUFFER_ADDRESS, 1*1024*1024) # Malloc buffer

    mu.ctl_exits_enabled(True)
    mu.ctl_set_exits([0x0])

    flashParser.parse(mu, FLASH)

    mu.mem_write(0x02000000, data)
    
    out_offset = 0x02000000 + len(data) + 0x10000

    mu.reg_write(UC_ARM_REG_R0, 0x02000000)        
    mu.reg_write(UC_ARM_REG_R1, out_offset)

    mu.reg_write(UC_ARM_REG_SP, 0x03040000)        

    mu.reg_write(UC_ARM_REG_APSR, 0xffffffff)
    mu.hook_add(UC_HOOK_CODE, hook_code, heap)
    
    for f in MEMCPY_ADDRESS+MALLOC_ADDRESS+FREE_ADDRESS+MEMSET_ADDRESS:
        mu.mem_write(f, ARM_RTS)

    mu.emu_start(0x1b860, 0x60000)
    
    temp = mu.mem_read(out_offset, length)    
    
    del mu
    gc.collect()

    return temp

def qmDecodeFrame(data, length):
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    heap = ucHeapLib.UnicornSimpleHeap(mu)

    mu.mem_map(0x0, 4*1024*1024) # Code
    mu.mem_map(0xa8000000, 4*1024*1024) # Code Ram
    mu.mem_map(0x02000000, 8*1024*1024) # Buffer
    mu.mem_map(0x03000000, 2*1024*1024) # Stack Pointer
    #mu.mem_map(MALLOC_BUFFER_ADDRESS, 1*1024*1024) # Malloc buffer

    mu.ctl_exits_enabled(True)
    mu.ctl_set_exits([0x0])

    flashParser.parse(mu, FLASH)

    mu.mem_write(0x02000000, data)
    
    out_offset = 0x02000000 + len(data) + 0x10000

    mu.reg_write(UC_ARM_REG_R0, 0x02000000)        
    mu.reg_write(UC_ARM_REG_R1, len(data))
    mu.reg_write(UC_ARM_REG_R2, out_offset)

    mu.reg_write(UC_ARM_REG_SP, 0x03040000)        

    mu.reg_write(UC_ARM_REG_APSR, 0xffffffff)
    mu.hook_add(UC_HOOK_CODE, hook_code, heap)
    
    for f in MEMCPY_ADDRESS+MALLOC_ADDRESS+FREE_ADDRESS+MEMSET_ADDRESS:
        mu.mem_write(f, ARM_RTS)

    mu.emu_start(0x1b94c, 0x60000)
    
    temp = mu.mem_read(out_offset, length)    
    
    del mu
    gc.collect()

    return temp

def qmDecodeAniFrame(data, length, count):
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    heap = ucHeapLib.UnicornSimpleHeap(mu)

    mu.mem_map(0x0, 4*1024*1024) # Code
    mu.mem_map(0xa8000000, 4*1024*1024) # Code Ram
    mu.mem_map(0x02000000, 8*1024*1024) # Buffer
    mu.mem_map(0x03000000, 2*1024*1024) # Stack Pointer
    #mu.mem_map(MALLOC_BUFFER_ADDRESS, 1*1024*1024) # Malloc buffer

    mu.ctl_exits_enabled(True)
    mu.ctl_set_exits([0x0])

    flashParser.parse(mu, FLASH)

    mu.mem_write(0x02000000, data)    
    
    out_offset = 0x02000000 + len(data) + 0x10000

    mu.reg_write(UC_ARM_REG_R0, 0x02000000)        
    mu.reg_write(UC_ARM_REG_R1, 1)
    mu.reg_write(UC_ARM_REG_R2, len(data))

    mu.reg_write(UC_ARM_REG_SP, 0x03040000)            

    mu.reg_write(UC_ARM_REG_APSR, 0xffffffff)
    mu.hook_add(UC_HOOK_CODE, hook_code, heap)
    
    for f in MEMCPY_ADDRESS+MALLOC_ADDRESS+FREE_ADDRESS+MEMSET_ADDRESS:
        mu.mem_write(f, ARM_RTS)

    mu.emu_start(0x1ba40, 0x60000)
    #print(mu.reg_read(UC_ARM_REG_R0))

    aniPtr = mu.reg_read(UC_ARM_REG_R0)
    assert aniPtr

    #print(mu.mem_read(aniPtr, 0x2000))
    #print("qm initialized")

    '''
    def on_invalid(mu, access, address, size, value, data):
        print("bad address", access, hex(address), size, hex(value))
        mu.mem_map(address, 2048)
        return True
    
    mu.hook_add(UC_HOOK_MEM_INVALID, on_invalid)
    '''

    '''
    def zb_mem(mu, access, address, size, value, data):
        print("zb mem", access, hex(address), size, hex(value))        
        return False
    
    mu.hook_add(UC_HOOK_MEM_WRITE, zb_mem, begin=0x00, end=0x800)
    '''

    frames = []

    for _ in range(count):        
        mu.reg_write(UC_ARM_REG_R0, aniPtr)
        mu.reg_write(UC_ARM_REG_R1, out_offset)
        mu.emu_start(0x1b9e8, 0x60000) 
        frames.append(mu.mem_read(out_offset, length))       

    #if not mu.reg_read(UC_ARM_REG_R0):
    #raise Exception("Failed to open QMG")    
            
    del mu
    gc.collect()

    return frames

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
    assert header[0xb] in [0x65, 0x95, 0x15], "Not a Swift/Anycall IFG file."
    assert header[0x9] in [0, 1], "Invalid codec type."

    width, height = struct.unpack("<HH", dataIn[4:8])

    if header[0xb] in [0x95, 0x15]:
        data = qmDecodeFrame(dataIn, (width*height*4))
        def splitAlphaRGB5658(data):
            alpha = []
            pixels = []

            offset = 0
            while offset<len(data):
                pixels.append(data[offset:offset+2])
                alpha.append(data[offset+2])
                offset += 3

            return pixels, alpha

        if header[0x10] == 0x0:
            if header[0x8] == 0x1:
                return Image.frombytes("RGB", (width, height), data, "raw", "BGR;16", 0, 1)
            elif header[0x8] == 0x2:
                return Image.frombytes("RGB", (width, height), data)
            elif header[0x8] == 0x3:
                return Image.frombytes("RGBA", (width, height), data)
            else:
                return Image.frombytes("RGB", (width, height), data, "raw", "BGR;16", 0, 1)
        else:
            pixData, pixAlph = splitAlphaRGB5658(data[:width*height*3])
            temp = Image.frombytes("RGB", (width, height), b"".join(pixData), "raw", "BGR;16", 0, 1).convert("RGBA")
            temp.putalpha(Image.frombytes("L", (width, height), bytes(pixAlph)))

            return temp

    else:
        data = vDecodeFrame(dataIn, (width*height*2))
        return Image.frombytes("RGB", (width, height), data, "raw", "BGR;16", 0, 1)