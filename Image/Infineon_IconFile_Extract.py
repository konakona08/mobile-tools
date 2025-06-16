from PIL import Image
from construct import *
import argparse
from io import BytesIO
import struct

palette8 = b"\x00\x00\x06\x00\x0C\x00\x13\x00\x19\x00\x1F\x00\x80\x01\x86\x01\x8C\x01\x93\x01\x99\x01\x9F\x01\x20\x03\x26\x03\x2C\x03\x33\x03\x39\x03\x3F\x03\xC0\x04\xC6\x04\xCC\x04\xD3\x04\xD9\x04\xDF\x04\x60\x06\x66\x06\x6C\x06\x73\x06\x79\x06\x7F\x06\xE0\x07\xE6\x07\xEC\x07\xF3\x07\xF9\x07\xFF\x07\x00\x30\x06\x30\x0C\x30\x13\x30\x19\x30\x1F\x30\x80\x31\x86\x31\x8C\x31\x93\x31\x99\x31\x9F\x31\x20\x33\x26\x33\x2C\x33\x33\x33\x39\x33\x3F\x33\xC0\x34\xC6\x34\xCC\x34\xD3\x34\xD9\x34\xDF\x34\x60\x36\x66\x36\x6C\x36\x73\x36\x79\x36\x7F\x36\xE0\x37\xE6\x37\xEC\x37\xF3\x37\xF9\x37\xFF\x37\x00\x60\x06\x60\x0C\x60\x13\x60\x19\x60\x1F\x60\x80\x61\x86\x61\x8C\x61\x93\x61\x99\x61\x9F\x61\x20\x63\x26\x63\x2C\x63\x33\x63\x39\x63\x3F\x63\xC0\x64\xC6\x64\xCC\x64\xD3\x64\xD9\x64\xDF\x64\x60\x66\x66\x66\x6C\x66\x73\x66\x79\x66\x7F\x66\xE0\x67\xE6\x67\xEC\x67\xF3\x67\xF9\x67\xFF\x67\x02\x00\x04\x00\x08\x00\x0A\x00\x0E\x00\x80\x00\x00\x01\x20\x02\xA0\x02\xA0\x03\x00\x10\x00\x20\x00\x40\x00\x50\x00\x70\x82\x10\x04\x21\x28\x42\xAA\x52\xAE\x73\x51\x8C\x55\xAD\xD7\xBD\xFB\xDE\x7D\xEF\x00\x88\x00\xA8\x00\xB8\x00\xD8\x00\xE8\x40\x04\x40\x05\xC0\x05\xE0\x06\x60\x07\x11\x00\x15\x00\x17\x00\x1B\x00\x1D\x00\x00\x98\x06\x98\x0C\x98\x13\x98\x19\x98\x1F\x98\x80\x99\x86\x99\x8C\x99\x93\x99\x99\x99\x9F\x99\x20\x9B\x26\x9B\x2C\x9B\x33\x9B\x39\x9B\x3F\x9B\xC0\x9C\xC6\x9C\xCC\x9C\xD3\x9C\xD9\x9C\xDF\x9C\x60\x9E\x66\x9E\x6C\x9E\x73\x9E\x79\x9E\x7F\x9E\xE0\x9F\xE6\x9F\xEC\x9F\xF3\x9F\xF9\x9F\xFF\x9F\x00\xC8\x06\xC8\x0C\xC8\x13\xC8\x19\xC8\x1F\xC8\x80\xC9\x86\xC9\x8C\xC9\x93\xC9\x99\xC9\x9F\xC9\x20\xCB\x26\xCB\x2C\xCB\x33\xCB\x39\xCB\x3F\xCB\xC0\xCC\xC6\xCC\xCC\xCC\xD3\xCC\xD9\xCC\xDF\xCC\x60\xCE\x66\xCE\x6C\xCE\x73\xCE\x79\xCE\x7F\xCE\xE0\xCF\xE6\xCF\xEC\xCF\xF3\xCF\xF9\xCF\xFF\xCF\x00\xF8\x06\xF8\x0C\xF8\x13\xF8\x19\xF8\x1F\xF8\x80\xF9\x86\xF9\x8C\xF9\x93\xF9\x99\xF9\x9F\xF9\x20\xFB\x26\xFB\x2C\xFB\x33\xFB\x39\xFB\x3F\xFB\xC0\xFC\xC6\xFC\xCC\xFC\xD3\xFC\xD9\xFC\xDF\xFC\x60\xFE\x66\xFE\x6C\xFE\x73\xFE\x79\xFE\x7F\xFE\xE0\xFF\xE6\xFF\xEC\xFF\xF3\xFF\xF9\xFF\xFF\xFF"


ImgHeader = Struct(
    "id" / Int16ul,
    "h" / Int16ul,
    "w" / Int16ul,
    "transp" / Int16ul,
    "bpp" / Int32ul,
)

ImgHeaderNew = Struct(
    "h" / Int16ul,
    "w" / Int16ul,
    "transp" / Int16ul,
    "bpp" / Int16ul,
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

def get_iconfile_icons(data):
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

def decode_icon(icon,byswap,newfmt):
    if newfmt:
        header = ImgHeaderNew.parse(icon)
        sz = ImgHeaderNew.sizeof()
    else:
        header = ImgHeader.parse(icon)
        sz = ImgHeader.sizeof()
    icon_data = icon[sz:]

    if header.bpp == 0:
        return None

    if header.bpp == 1:
        return bpp1_to_pil(icon_data, header.w, header.h)
    else:
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

        if header.bpp == 8:
            bpp16_data = bytearray(header.w*header.h*2) #convert to rgb565 from palette8
            for i in range(header.w*header.h):
                bpp16_data[i<<1] = palette8[icon_data[i]*2]
                bpp16_data[i<<1+1] = palette8[icon_data[i]*2+1]
            
            im = Image.frombytes("RGB", (header.w, header.h), bytes(bpp16_data),"raw", "BGR;16")
        elif header.bpp == 16:
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
                    bpp16_data[i*2] = icon_data[i*2+1]
                    bpp16_data[i*2+1] = icon_data[i*2]
            else:
                bpp16_data = icon_data
            
            im = Image.frombytes("RGB", (header.w, header.h), bytes(bpp16_data),"raw", "BGR;16")
        if transVal:
            riTmp = im.convert("RGBA").getdata()
            rFin = []
            
            for ri in riTmp:
                if ri[:3] == transVal:
                    transp = 2
                    rFin.append((255,255,255,0))
                else:
                    rFin.append(ri)
                
            im = im.convert("RGBA")
            im.putdata(rFin)

        return im

if __name__ == "__main__":
    ap = argparse.ArgumentParser("iconfile")
    
    ap.add_argument("--byteswap", "-b", help="Byteswap (16-bit images)", action="store_true")
    ap.add_argument("--new", "-n", help="New format (skip 2 bytes)", action="store_true")
    ap.add_argument("in_file")

    args = ap.parse_args()

    data = open(args.in_file, "rb").read()

    icons = get_iconfile_icons(data)

    for a in range(len(icons)):
        decoded = decode_icon(icons[a], args.byteswap, args.new)
        
        if decoded:
            decoded.save(f"{args.in_file}_{a}.png")