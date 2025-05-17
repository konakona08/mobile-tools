import struct
import os
import sys
from construct import *
from PIL import Image

RUNEHeader = Struct (
        "magic" / Bytes(4), #4bytes
        "width" / Int32ul,
        "height" / Int32ul,
        "bpp" / Int32ul
)

if len(sys.argv) < 2:
        print(f"Not enough arguments! usage: {sys.argv[0]} file", file=sys.stderr)
        sys.exit(1)

fd = open(sys.argv[1], "rb")
size = os.path.getsize(sys.argv[1])
header = RUNEHeader.parse(fd.read(RUNEHeader.sizeof()))
if header.magic != b'RUNE':
        print("Cannot convert the image. Not in LG RUNE format.")
        sys.exit(1)
outp = bytearray()
while fd.tell() < size:
	pixel = fd.read(2)
	len = struct.unpack("<H", fd.read(2))[0]
	outp += pixel*len
	if header.bpp == 16:
		imTmp = Image.frombytes("RGB", (header.width, header.height), bytes(outp) ,"raw", "BGR;16")
		imTmp.save(f"{sys.argv[1]}.png")          
fd.close()
