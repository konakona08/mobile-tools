import struct
import os
import zlib, sys
from PIL import Image

zlib_mode = False

if len(sys.argv) < 1:
        print(f"Not enough arguments! usage: {sys.argv[0]} file", file=sys.stderr)
        sys.exit(1)

fd = open(sys.argv[1], "rb")
magic = fd.read(4)
if magic == b'RI\0\0':
        zlib_mode = True
else:
        if magic == b'NA\0\0':
                zlib_mode = False
        else:
                print("Cannot convert the animation. Not in Huawei .ani format.")
                sys.exit(1)

hdr_sz, frames, speed, height, width, bpp = struct.unpack("<LHHLLL", fd.read(20))
if hdr_sz < 20:
        print("Invalid hdr size")
        sys.exit(1)	

my_imgs = []

for i in range(int(frames)):
        if zlib_mode == True:
                datasize = struct.unpack("<L", fd.read(4))[0]
                data = zlib.decompress(fd.read(datasize))
        else:
                data = fd.read(int(width*height*bpp/8))
        if bpp == 1:
                imTmp = Image.frombytes("1", (width, height), bytes(data) ,"raw")
        if bpp == 16:
                imTmp = Image.frombytes("RGB", (width, height), bytes(data) ,"raw", "BGR;16")
        my_imgs.append(imTmp)

my_imgs[0].save(f"{sys.argv[1]}.gif", save_all=True, append_images=my_imgs[1:], optimize=False, duration=speed, loop=0)	
fd.close()
