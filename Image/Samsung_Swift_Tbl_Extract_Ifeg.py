from construct import *
import os

Entry = Struct(
    "off" / Int32ul,
    "idx" / Int32ul
)

if __name__ == "__main__":
    import sys
    fd = open(sys.argv[1], "rb")
    off = int(sys.argv[2], 16)
    cnt = int(sys.argv[3])
    if not (os.path.exists(sys.argv[4])):
        os.mkdir(sys.argv[4])
    entries = []
    fd.seek(off)
    for a in range(cnt):
        entries.append(Entry.parse(fd.read(Entry.sizeof())))
    fd.seek(0)
    dtbuf = fd.read()
    
    for i, entry in enumerate(entries):
        entry.off -= 0x20000000
        print(f"Processing entry {i} at offset {entry.off:08x}")
        if dtbuf[entry.off:entry.off+4] != b"IFEG":
            continue
        nextifeg = dtbuf.find(b"IFEG", entry.off+1)
        if nextifeg == -1:
            nextifeg = len(dtbuf)
        data = dtbuf[entry.off:nextifeg]
        with open(f"{sys.argv[4]}/{entry.idx}.ifg", "wb") as f:
            f.write(data)