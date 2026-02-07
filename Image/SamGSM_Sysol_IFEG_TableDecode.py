from construct import Struct, Int32ul
from Modules import Imaster_IFEG
import sys
import os
import argparse

Entry = Struct(
    "idx" / Int32ul,
    "off" / Int32ul
)

def hex_int(value):
    return int(value, 16)

if __name__ == "__main__":
    ap = argparse.ArgumentParser("sysol_ifegtblfind")
    
    ap.add_argument("in_file")
    ap.add_argument("offset", type=hex_int)
    ap.add_argument("out_folder")

    args = ap.parse_args()

    if not (os.path.exists(args.out_folder)):
        os.mkdir(args.out_folder)

    fd = open(args.in_file, "rb")
    
    fd.seek(args.offset)
    entries = []
    while True:
        entry = Entry.parse(fd.read(Entry.sizeof()))
        if entry.idx == 65535:
            break
        entries.append(entry)

    for i, entry in enumerate(entries):
        entry.off -= 0x20000000
        print(f"Processing entry {i} at offset {entry.off:08x}")
        fd.seek(entry.off)
        data = fd.read()
        if data[:0x4] != b"IFEG":
            continue
        img = Imaster_IFEG.ifgDecode(data)
        img.save(f"{args.out_folder}/IMG_{i}.png")
    fd.close()