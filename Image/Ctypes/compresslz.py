from . import FindArch
import ctypes
import os
import argparse
import struct

###determine os first
os_bits = FindArch.get_platform()

file_to_load = "libCompressLZ" + str(os_bits) + ".dll"

try:
    a = ctypes.CDLL(os.path.join(os.path.dirname(__file__), file_to_load))
except Exception:
    print("Failed to load library")
    exit(1)

# void* my_malloc(size_t size)
my_malloc = a.my_malloc
my_malloc.argtypes = [ctypes.c_size_t]
my_malloc.restype = ctypes.c_void_p

# void my_free(void* ptr)
my_free = a.my_free
my_free.argtypes = [ctypes.c_void_p]
my_free.restype = None

# unsigned int decompress(unsigned char* src, unsigned char* pWrite)
decompress = a.decompress
decompress.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
decompress.restype = ctypes.c_uint

# unsigned int decompress_big(unsigned char* src, unsigned char* pWrite)
decompress_big = a.decompress_big
decompress_big.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
decompress_big.restype = ctypes.c_uint

def ptr_to_byte(ptr, size):
	data = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte))
	return bytearray(data[:size])

class CompressLZ:
	def __init__(self):
		pass

	def unpack_get_cmd_size(self, inp):
		sz = struct.unpack(">H", inp[:2])[0]
		if inp[1] & 1:
			sz |= struct.unpack("<H", inp[2:4])[0] << 15
		sz &= 0xfffffffe
		return sz

	def unpack_get_cmd(self, cmd, endian):
		if endian == True:
			cmdv = struct.unpack("<H", cmd[:2])[0]
		else:
			cmdv = struct.unpack(">H", cmd[:2])[0]
		return cmdv

	def unpack_get_size(self, inp: bytes, sz: int, endian: bool) -> (bool, int):
		if not inp or sz == 0:
			return False, 0
		if inp[:12] != b"compress LZ\x00":
			return False, 0
		inp2 = inp[0x10:]
		csize = self.unpack_get_cmd_size(inp2)
		extd_sz = inp2[1] & 1
		inp2 = inp2[4:] if (extd_sz) else inp2[2:]
		cmd = inp2
		cmd_sz_curr = 0
		dat = cmd[csize:]
		esize = 0
		# Process command values
		while cmd_sz_curr<csize:
			cmdv = self.unpack_get_cmd(cmd, endian)
			cmd = cmd[2:]
			esize += (cmdv >> 12)<<1
			cmd_sz_curr+=2

		esize += (sz-16-(4 if extd_sz==1 else 2)-csize)

		return True, esize

	def unpack(self, inp: bytes, sz: int, endian: bool) -> bytes:
		if not inp or sz == 0:
			return b""
		if inp[:12] != b"compress LZ\x00":
			return b""
		
		szout = self.unpack_get_size(inp,sz,endian)[1]

		buffer = my_malloc(szout)

		print(f"{buffer:16x}")

		if buffer == 0:
			return b""
		
		if endian == False:
			decompress(inp, buffer)
		else:
			decompress_big(inp, buffer)

		data = ptr_to_byte(buffer, szout)
		my_free(buffer)
		return data


if __name__ == "__main__":
    ap = argparse.ArgumentParser("compresslz")
    
    ap.add_argument("--big", "-b", help="Big endian", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("in_file")
    ap.add_argument("out_file")

    args = ap.parse_args()

    clz = CompressLZ()
    with open(args.out_file, "wb") as f:
        f.write(clz.unpack(open(args.in_file, "rb").read(), os.path.getsize(args.in_file), args.big))
