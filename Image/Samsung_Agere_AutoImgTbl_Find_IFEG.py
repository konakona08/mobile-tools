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
        img = Imaster_IFEG_Agere.ifgDecode(ftmp[entry.offs:])
        if img:
            img.save(f"{args.out_folder}/IMG_{i}.png")