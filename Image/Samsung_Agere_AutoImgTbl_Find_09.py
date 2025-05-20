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
            
if __name__ == "__main__":
    ap = argparse.ArgumentParser("agere_itblfind")
    
    ap.add_argument("in_file")
    ap.add_argument("disp_width", type=int)
    ap.add_argument("disp_height", type=int)
    ap.add_argument("out_folder")
    
    args = ap.parse_args()

    if not (os.path.exists(args.out_folder)):	os.mkdir(args.out_folder)	

    ftmp = open(args.in_file, "rb").read()
    
    offset = ftmp.find(struct.pack("<HH", args.disp_width, args.disp_height))
    found = False
    while True:
        if ftmp[offset+8:offset+12] == struct.pack("<HH", args.disp_width, args.disp_height):
            #########find starting tbl entry
            while True:
                entry_tmp = Entry.parse(ftmp[offset:offset+Entry.sizeof()])
                if entry_tmp.width == 0 and entry_tmp.height == 0 and entry_tmp.offs == 0:
                    found = True
                    break
                offset -= Entry.sizeof()
        else:
            offset = ftmp.find(struct.pack("<HH", args.disp_width, args.disp_height), offset+8)
        if found:
            break
        if offset == -1:
            break

    offset += 8

    entries = parse_entries(ftmp, offset)

    for i, entry in enumerate(entries):
        print(f"Processing entry {i} at offset {entry.offs:08x}")
        img = decode_09(ftmp[entry.offs:], entry.width, entry.height)
        if img:
            img.save(f"{args.out_folder}/IMG_{i}.png")