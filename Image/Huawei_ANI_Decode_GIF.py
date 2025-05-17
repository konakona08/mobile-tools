import struct
import os
import zlib, sys
from PIL import Image

zlib_mode = False

AniHeader = Struct(
        "magic" / Bytes(4),
        "hdr_sz" / Int32ul,
        "frames" / Int16ul,
        "speed" / Int16ul,
        "height" / Int32ul,
        "width" / Int32ul,
        "bpp" / Int32ul
)

if __name__ == "__main__":
        if len(sys.argv) < 1:
                print(f"Not enough arguments! usage: {sys.argv[0]} file", file=sys.stderr)
                sys.exit(1)

        fd = open(sys.argv[1], "rb")

        header = AniHeader.parse(fd.read(AniHeader.sizeof()))

        assert(header.magic == b'RI\0\0' or header.magic == b'NA\0\0')
        assert(header.hdr_sz >= 20)

        if header.magic == b'RI\0\0':
                zlib_mode = True
        else:
                zlib_mode = False

        my_imgs = []

        for i in range(int(header.frames)):
                if zlib_mode == True:
                        datasize = struct.unpack("<L", fd.read(4))[0]
                        data = zlib.decompress(fd.read(datasize))
                else:
                        data = fd.read(int(header.width*header.height*header.bpp/8))
                if header.bpp == 1:
                        imTmp = Image.frombytes("1", (header.width, header.height), bytes(data) ,"raw")
                if header.bpp == 16:
                        imTmp = Image.frombytes("RGB", (header.width, header.height), bytes(data) ,"raw", "BGR;16")
                my_imgs.append(imTmp)

        my_imgs[0].save(f"{sys.argv[1]}.gif", save_all=True, append_images=my_imgs[1:], optimize=False, duration=header.speed, loop=0)	
        fd.close()
