from construct import *
from PIL import Image
import argparse
import os
import struct
from io import BytesIO

Entry = Struct(
    "width" / Int16ul,
    "height" / Int16ul,
    "offs" / Int32ul
)

def decode_09(data, width, height):
    out_size = 0
    palette = [0]*256
    out_img = bytearray(width*height*2)
    data_io = BytesIO(data)
    header = data_io.read(1)[0]
    if header not in [0x09,0x4f,0x3b]:
        return None #don't error out
    palette_colors = data_io.read(1)[0]
    for i in range(palette_colors):
        palette[i] = struct.unpack("<H",data_io.read(2))[0]
    while out_size < width*height*2:
        cmd = data_io.read(1)[0]
        count = cmd & 0x3f
        if cmd & 0x80:
            if cmd & 0x40:
                pixel = palette[data_io.read(1)[0]]
            else:
                pixel = struct.unpack("<H",data_io.read(2))[0]
            for i in range(count):
                out_img[out_size:out_size+2] = struct.pack("<H", pixel)
                out_size += 2
        else:
            for i in range(count):
                if cmd & 0x40:
                    pixel = palette[data_io.read(1)[0]]
                else:
                    pixel = struct.unpack("<H",data_io.read(2))[0]
                out_img[out_size:out_size+2] = struct.pack("<H", pixel)
                out_size += 2
    return Image.frombytes("RGB", (width, height), out_img, "raw", "BGR;16")

def parse_entries(bdata, offset):
    entries = []
    while True:
        entry = Entry.parse(bdata[offset:offset+Entry.sizeof()])
        if entry.width == 0 and entry.height == 0 and entry.offs == 0:
            break
        entries.append(entry)
        offset += Entry.sizeof()
    return entries

def hex_int(value):
    return int(value, 16)

def find_tbl(ftmp, start, disp_width, disp_height):
    offset = ftmp.find(struct.pack("<HH", disp_width, disp_height), start)
    found = False
    while True:
        if ftmp[offset+8:offset+12] == struct.pack("<HH", disp_width, disp_height):
            #########find starting tbl entry
            while True:
                entry_tmp = Entry.parse(ftmp[offset:offset+Entry.sizeof()])
                if entry_tmp.width == 0 and entry_tmp.height == 0 and entry_tmp.offs == 0:
                    #if the entry before the previous entry's w&h combined is something >= 0x3000000 and not < 0x20000000
                    #then it's not the correct table (SGH-E715; E75UVWK4)
                    #This also applies to offsets < 0x20 (SGH-S300; S30XEWB1)
                    temp = struct.unpack("<I", ftmp[offset-8:offset-4])[0]
                    temp2 = struct.unpack("<I", ftmp[offset-4:offset])[0]
                    if (temp < 0x3000000 and temp2 < 0x20) or (temp >= 0x3000000 and temp < 0x20000000):
                        found = False
                        temp_len = len(parse_entries(ftmp, offset+8))*Entry.sizeof()
                        return find_tbl(ftmp, offset + temp_len, disp_width, disp_height)
                    found = True
                    break
                offset -= Entry.sizeof()
        else:
            offset = ftmp.find(struct.pack("<HH", disp_width, disp_height), offset+8)
        if found:
            break
        if offset == -1:
            break
    return offset

if __name__ == "__main__":
    ap = argparse.ArgumentParser("agere_itblfind")
    
    ap.add_argument("in_file")
    ap.add_argument("disp_width", type=int)
    ap.add_argument("disp_height", type=int)
    ap.add_argument("out_folder")
    ap.add_argument("--doffset", "-d", type=hex_int, default=0, help="Offset of image in memory")
    
    args = ap.parse_args()
    
    doffset = args.doffset

    if not (os.path.exists(args.out_folder)):	os.mkdir(args.out_folder)	

    ftmp = open(args.in_file, "rb").read()

    offset = find_tbl(ftmp, 0, args.disp_width, args.disp_height)

    offset += 8

    print(f"Found table at offset {offset:08x}")

    entries = parse_entries(ftmp, offset)

    for i, entry in enumerate(entries):
        print(f"Processing entry {i} at offset {entry.offs:08x}")
        try:
            img = decode_09(ftmp[(entry.offs-doffset):], entry.width, entry.height)
            if img:
                img.save(f"{args.out_folder}/IMG_{i}.png")
        except:
            pass