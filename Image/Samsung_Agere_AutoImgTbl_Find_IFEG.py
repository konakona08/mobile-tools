from construct import *
from PIL import Image
import argparse
import os
import struct
from io import BytesIO
from Modules import Imaster_IFEG_Agere

Entry = Struct(
    "width" / Int16ul,
    "height" / Int16ul,
    "offs" / Int32ul
)

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
        try:
            img = Imaster_IFEG_Agere.ifgDecode(ftmp[entry.offs-doffset:])
            if img:
                img.save(f"{args.out_folder}/IMG_{i}.png")
        except:
            pass
