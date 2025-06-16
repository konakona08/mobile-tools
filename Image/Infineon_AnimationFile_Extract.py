from PIL import Image
from construct import *
import argparse
from io import BytesIO
import struct

AnimHeader = Struct(
    "id" / Int16ul,
    "ms" / Int16ul,
    "frames" / Int8ul,
    "bpp" / Int8ul,
    "padding" / Padding(2)
)

ImgHeader = Struct(
    "h" / Int16ul,
    "w" / Int16ul,
    "transp" / Int32ul
)

def bpp1_to_pil(img_data, wdt, hgt):
    rows = (hgt + 7) // 8  # This is equivalent to ceil(hgt/8)
    img = Image.new('1', (wdt, hgt))
    pixels = img.load()

    for x in range(wdt):
        for y in range(rows):
            try:
                byte = img_data[wdt * y + x]
                for bit in range(8):
                    y_pos = y*8+bit
                    if y_pos < hgt :
                        pixels[x, y_pos] = ((byte >> bit) & 1) == 0
            except:
                for bit in range(8):
                    y_pos = y*8+bit
                    if y_pos < hgt :
                        pixels[x, y_pos] = 0

    return img

def get_animationfile_anims(data):
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

def get_anim_frames(data):
    offs = []
    out = []

    hdr = AnimHeader.parse(data)

    data_read = BytesIO(data[AnimHeader.sizeof():])
    cnt = hdr.frames
    
    for c in range(cnt):
        off = struct.unpack("<L", data_read.read(4))[0]
        offs.append(off)
    
    for c in range(cnt):
        if c == cnt-1:
            noffs = len(data)
        else:
            noffs = offs[c+1]
        
        data_read.seek(offs[c]+(cnt*4))
        out.append(data_read.read(noffs-offs[c]))
    
    return [hdr, out]

def decode_anim_frame(frame,bpp,byswap):
    header = ImgHeader.parse(frame)
    frame_data = frame[ImgHeader.sizeof():]
    if bpp == 1:
        return bpp1_to_pil(frame_data, header.w, header.h)
    elif bpp == 16:
        ##get alpha color for transparent pixels
        r = (((header.transp>>11)&0x1f)<<3)
        if r!= 0:
            r+=7
        g = (((header.transp>>5)&0x3f)<<2)
        if g!= 0:
            g+=3
        b = ((header.transp&0x1f)<<3)
        if b!= 0:
            b+=7
        transVal = [r,g,b]
        transVal = tuple(transVal)

        bpp16_data = bytearray(header.w*header.h*2)
        if byswap:
            for i in range(header.w*header.h):
                bpp16_data[i*2] = frame_data[i*2+1]
                bpp16_data[i*2+1] = frame_data[i*2]
        else:
            bpp16_data = frame_data
        
        im = Image.frombytes("RGB", (header.w, header.h), bytes(bpp16_data),"raw", "BGR;16")
        if transVal:
            riTmp = im.convert("RGBA").getdata()
            rFin = []
            
            for ri in riTmp:
                #print(ri[:3], transVal)
                if ri[:3] == transVal:
                    transp = 2
                    rFin.append((255,255,255,0))
                else:
                    rFin.append(ri)
			
            im = im.convert("RGBA")
            im.putdata(rFin)

        return im

if __name__ == "__main__":
    ap = argparse.ArgumentParser("animationfile")
    
    ap.add_argument("--byteswap", "-b", help="Byteswap (16-bit images)", action="store_true")
    ap.add_argument("in_file")

    args = ap.parse_args()

    data = open(args.in_file, "rb").read()

    anims = get_animationfile_anims(data)

    for a in range(len(anims)):
        decoded = []
        anim_frames = get_anim_frames(anims[a])
        
        for f in range(len(anim_frames[1])):
            decoded.append(decode_anim_frame(anim_frames[1][f], anim_frames[0].bpp, args.byteswap))

        decoded[0].save(f"{args.in_file}_{a}.gif", save_all=True, append_images=decoded[1:], optimize=False, duration=anim_frames[0].ms, loop=0)