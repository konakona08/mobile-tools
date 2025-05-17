import struct
import os
import zlib, sys
from PIL import Image

ImageHeader = Struct(
        "magic" / Bytes(4),
        "datasize" / Int32ul,
        "width" / Int16ul,
        "height" / Int16ul,
        "uncsize" / Int32ul,
        "bpp" / Int16ul
)

if __name__ == "__main__":
        if len(sys.argv) < 1:
                print(f"Not enough arguments! usage: {sys.argv[0]} file", file=sys.stderr)
                sys.exit(1)

        fd = open(sys.argv[1], "rb")
        header = ImageHeader.parse(fd.read(ImageHeader.sizeof()))
        if header.magic != b'ZLIB':
                print("Cannot convert the image. Not in Alcatel ZLIB format.")
                sys.exit(1)
        data = fd.read(header.datasize)
        unc_data = zlib.decompress(data)
        assert(header.uncsize == len(unc_data))
        if header.bpp == 16:
                imTmp = Image.frombytes("RGB", (header.width, header.height), bytes(unc_data) ,"raw", "BGR;16")
                imTmp.save(f"{sys.argv[1]}.png")
        fd.close()
