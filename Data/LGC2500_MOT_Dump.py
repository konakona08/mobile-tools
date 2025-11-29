from construct import *
import os
import struct

Entry = Struct(
        "offset" / Int32ul,
        "size" / Int32ul,
        "filename" / Bytes(20)
)

def get_entries(fd):
    entries = []
    entry_count = fd.read(1)[0]-0x30
    for i in range(entry_count):
        curr_entry = Entry.parse(fd.read(Entry.sizeof()))
        #########Byswap#########
        curr_entry.offset = struct.unpack("<L", curr_entry.offset.to_bytes(4, "big"))[0]
        curr_entry.size = struct.unpack("<L", curr_entry.size.to_bytes(4, "big"))[0]
        temp = bytearray()
        for a in range(20):
            if curr_entry.filename[a] != 0xff:
                temp.append(curr_entry.filename[a])
            else:
                break
        curr_entry.filename = temp.decode("ascii")
        entries.append(curr_entry)
    return entries


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Not enough arguments! usage: {sys.argv[0]} <mot file>", file=sys.stderr)
        sys.exit(1)
    fd = open(sys.argv[1], "rb")
    if not (os.path.exists(sys.argv[1] + "_ext")):
        os.mkdir(sys.argv[1] + "_ext")
    entries = get_entries(fd)
    for i, entry in enumerate(entries):
        print(f"Processing entry {i} at offset {entry.offset:08x}, size {entry.size:08x}, filename {entry.filename}")
        fd.seek(entry.offset)
        data = fd.read(entry.size)
        with open(f"{sys.argv[1]}_ext/{entry.filename}", "wb") as f:
            f.write(data)