from construct import *
from io import BytesIO
import struct

ImageHeader = Struct(
    "total_size" / Int32ul,
    "width" / Int16ul,
    "height" / Int16ul,
    "is_prev" / Int8ul
)

def decode(in_data, out_data):
    header = ImageHeader.parse(in_data)
    in_data = BytesIO(in_data[ImageHeader.sizeof():])
    osize = header.width * header.height * 2

    dec_size = 0

    cmd = 0

    while dec_size < osize:
        if not cmd & 256:            
            cmd = 0xff00 | in_data.read(1)[0]

        is_literal = cmd&1
        if is_literal:
            out_data[dec_size] = in_data.read(1)[0]
            dec_size += 1
        else:
            if header.is_prev:
                cmd2 = in_data.read(1)[0]
                
                skip_match = cmd2>>7
                if skip_match:
                    long = ((cmd2>>6)&1)
                    if long:
                        offs += ((cmd2&0x3f)<<8) | in_data.read(1)[0]
                    else:
                        offs += cmd2&0x3f
                else:
                    cmd3 = in_data.read(1)[0]
                    count = (cmd3 & 0xf) + 3
                    relative = (cmd3>>4)<<7 | (cmd2&0x7f)
                    for _ in range(count):
                        out_data[dec_size] = out_data[dec_size-relative]
                        dec_size += 1
            else:
                cmd2,cmd3 = struct.unpack("<BB", in_data.read(2))
                count = (cmd3 & 0x1f) + 3
                relative = (cmd3>>5)<<8 | cmd2
                for _ in range(count):
                    out_data[dec_size] = out_data[dec_size-relative]
                    dec_size += 1
        
        cmd>>=1