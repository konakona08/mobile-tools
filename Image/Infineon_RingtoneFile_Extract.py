from doctest import REPORTING_FLAGS
from PIL import Image
from construct import *
import argparse
from io import BytesIO
import struct
import os

RING_DEST_MSG = 0x1
RING_DEST_RING = 0x2
RING_DEST_POWER = 0x8

RingHeader = Struct(
    "size" / Int32ul,
    "id" / Int16ul,
    "fmt" / Int8ul,
    "dest" / Int8ul
)

RingHeaderNew = Struct(
    "size" / Int32ul,
    "fmt" / Int8ul,
    "dest" / Int8ul,
    "padding" / Padding(2)
)

def get_ringtonefile_rings(data):
    offs = []
    out = []

    data_read = BytesIO(data)
    cnt = struct.unpack("<L", data_read.read(4))[0]
    
    for c in range(cnt):
        off = struct.unpack("<L", data_read.read(4))[0]
        offs.append(off)
    
    for c in range(cnt):
        if c == cnt-1:
            noffs = len(data)
        else:
            noffs = offs[c+1]
        
        data_read.seek(offs[c]+((cnt+1)*4))
        out.append(data_read.read(noffs-offs[c]))
    
    return out

def process_ring(ring, newfmt):
    if newfmt:
        header = RingHeaderNew.parse(ring)
        sz = RingHeaderNew.sizeof()
    else:
        header = RingHeader.parse(ring)
        sz = RingHeader.sizeof()
    ring_data = ring[sz:]
    name = ring_data[:64].decode("utf_16").rstrip('\x00')
    data = ring_data[64:64+header.size]
    
    if data[:4] == b"RIFF":
        ext = "wav"
    elif data[:4] == b"MThd":
        ext = "mid"
    elif data[:5] == b"#!AMR":
        ext = "amr"
    else:
        ext = "bin"

    if header.dest & RING_DEST_MSG:
        dest = "message"
    elif header.dest & RING_DEST_RING:
        dest = "ringtone"
    elif header.dest & RING_DEST_POWER:
        dest = "power"
    else:
        dest = "system"

    return name, ext, dest, data

if __name__ == "__main__":
    ap = argparse.ArgumentParser("ringtonefile")
    
    ap.add_argument("in_file")
    ap.add_argument("--new-fmt", "-n", help="New format (skip 2 bytes)", action="store_true")

    args = ap.parse_args()

    data = open(args.in_file, "rb").read()

    rings = get_ringtonefile_rings(data)

    for a in range(len(rings)):
        name, ext, dest, ring_data = process_ring(rings[a], args.new_fmt)
        #write to specific folder
        os.makedirs(f"{args.in_file}_{dest}", exist_ok=True)
        open(f"{args.in_file}_{dest}/{name}.{ext}", "wb").write(ring_data)