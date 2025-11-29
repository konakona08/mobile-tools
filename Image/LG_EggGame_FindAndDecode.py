import os
import sys
from io import BytesIO
import struct
from PIL import Image

def decode_img(img):
    img_reader = BytesIO(img)
    assert img_reader.read(2) == b"EG"
    wdt,hgt,x,y,palette_size,fmt,alpha = struct.unpack("<HHHHHBB", img_reader.read(12))
    enc_fmt = fmt&0xf
    if (enc_fmt == 1 or enc_fmt == 10):
        mask = 0x80
        bits = 1
        read_bits = 8
    elif (enc_fmt == 2 or enc_fmt == 11):
        mask = 0xc0
        bits = 2
        read_bits = 4
    elif (enc_fmt == 3 or enc_fmt == 12):
        mask = 0xf0
        bits = 4
        read_bits = 2
    elif (enc_fmt == 0 or enc_fmt == 4 or enc_fmt == 13):
        mask = 0xff
        bits = 8
        read_bits = 1
    ###########get aligned width
    align_wdt = wdt
    if bits == 1:
        if wdt & 7:
            align_wdt += 8 - (wdt & 7)
    elif bits == 2:
        if wdt & 3:
            align_wdt += 4 - (wdt & 3)
    elif bits == 4:
        if wdt & 1:
            align_wdt += 1 - (wdt & 1)
    print(align_wdt, bits)
    palette = img[14:14+palette_size]
    #######cvt
    palette_16 = []
    for i in range(palette_size>>1):
        palette_16.append(palette[i*2]|(palette[i*2+1]<<8))
    data = img[14+palette_size:]
    off_curr = 0
    read_pixel_curr = 0
    mask_curr = 0
    out_img = Image.new("RGBA", (align_wdt,hgt))
    tmp_8bpp_decoded = []
    sz = 0
    ##########decode to 8bpp array
    while sz<hgt*align_wdt:
        for t in range(read_bits):
            pixel = data[off_curr]
            pixel = (pixel & mask_curr) >> (8-((read_pixel_curr+1)*bits))
            read_pixel_curr += 1
            mask_curr >>= bits
            sz+=1
            #######do not add pixel if close to end of row
            tmp_8bpp_decoded.append(pixel)
        if read_pixel_curr == read_bits:
            read_pixel_curr = 0
            off_curr += 1
            mask_curr = mask
    ##########write to new image
    for y in range(hgt):
        for x in range(align_wdt):
            pixel_rgb565 = palette_16[tmp_8bpp_decoded[y*align_wdt+x]]
            out_img.putpixel((x,y), ((pixel_rgb565>>11<<3), ((pixel_rgb565>>5)&0x3f)<<2, (pixel_rgb565&0x1f)<<3, 255))
    ######crop img
    out_img = out_img.crop((0,0,wdt,hgt))
    return out_img

def main():
	if len(sys.argv) < 2:
		print("Not enough arguments")
		sys.exit(1)
	ftmp = bytearray()
	inp = open(sys.argv[1], "rb")
	dtbuf = inp.read()
	while dtbuf != b"":
		ftmp += dtbuf
		dtbuf = inp.read()
	offset = ftmp.find(b"EG")
	if not (os.path.exists(sys.argv[1] + "_ext_img")):	os.mkdir(sys.argv[1] + "_ext_img")	
	cnt = 0	
	while offset != -1:
		cnt += 1
		nextRUNE = ftmp.find(b"EG", offset+1)
		if nextRUNE == -1:
			nextRUNE = None
		img = decode_img(ftmp[offset:nextRUNE])
		img.save(f"{sys.argv[1]}_ext_img/IMG_{cnt}.png")
		offset = ftmp.find(b"EG", offset+1)	

if __name__ == "__main__":
	main()
