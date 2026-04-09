import argparse
from PIL import Image
import struct

RGB332 = b"\x00\x00\x00\x00\x00\x55\x00\x00\xaa\x00\x00\xff\x00\x24\x00\x00\x24\x55\x00\x24\xaa\x00\x24\xff\x00\x48\x00\x00\x48\x55\x00\x48\xaa\x00\x48\xff\x00\x6c\x00\x00\x6c\x55\x00\x6c\xaa\x00\x6c\xff\x00\x90\x00\x00\x90\x55\x00\x90\xaa\x00\x90\xff\x00\xb4\x00\x00\xb4\x55\x00\xb4\xaa\x00\xb4\xff\x00\xd8\x00\x00\xd8\x55\x00\xd8\xaa\x00\xd8\xff\x00\xfc\x00\x00\xfc\x55\x00\xfc\xaa\x00\xfc\xff\x24\x00\x00\x24\x00\x55\x24\x00\xaa\x24\x00\xff\x24\x24\x00\x24\x24\x55\x24\x24\xaa\x24\x24\xff\x24\x48\x00\x24\x48\x55\x24\x48\xaa\x24\x48\xff\x24\x6c\x00\x24\x6c\x55\x24\x6c\xaa\x24\x6c\xff\x24\x90\x00\x24\x90\x55\x24\x90\xaa\x24\x90\xff\x24\xb4\x00\x24\xb4\x55\x24\xb4\xaa\x24\xb4\xff\x24\xd8\x00\x24\xd8\x55\x24\xd8\xaa\x24\xd8\xff\x24\xfc\x00\x24\xfc\x55\x24\xfc\xaa\x24\xfc\xff\x48\x00\x00\x48\x00\x55\x48\x00\xaa\x48\x00\xff\x48\x24\x00\x48\x24\x55\x48\x24\xaa\x48\x24\xff\x48\x48\x00\x48\x48\x55\x48\x48\xaa\x48\x48\xff\x48\x6c\x00\x48\x6c\x55\x48\x6c\xaa\x48\x6c\xff\x48\x90\x00\x48\x90\x55\x48\x90\xaa\x48\x90\xff\x48\xb4\x00\x48\xb4\x55\x48\xb4\xaa\x48\xb4\xff\x48\xd8\x00\x48\xd8\x55\x48\xd8\xaa\x48\xd8\xff\x48\xfc\x00\x48\xfc\x55\x48\xfc\xaa\x48\xfc\xff\x6c\x00\x00\x6c\x00\x55\x6c\x00\xaa\x6c\x00\xff\x6c\x24\x00\x6c\x24\x55\x6c\x24\xaa\x6c\x24\xff\x6c\x48\x00\x6c\x48\x55\x6c\x48\xaa\x6c\x48\xff\x6c\x6c\x00\x6c\x6c\x55\x6c\x6c\xaa\x6c\x6c\xff\x6c\x90\x00\x6c\x90\x55\x6c\x90\xaa\x6c\x90\xff\x6c\xb4\x00\x6c\xb4\x55\x6c\xb4\xaa\x6c\xb4\xff\x6c\xd8\x00\x6c\xd8\x55\x6c\xd8\xaa\x6c\xd8\xff\x6c\xfc\x00\x6c\xfc\x55\x6c\xfc\xaa\x6c\xfc\xff\x90\x00\x00\x90\x00\x55\x90\x00\xaa\x90\x00\xff\x90\x24\x00\x90\x24\x55\x90\x24\xaa\x90\x24\xff\x90\x48\x00\x90\x48\x55\x90\x48\xaa\x90\x48\xff\x90\x6c\x00\x90\x6c\x55\x90\x6c\xaa\x90\x6c\xff\x90\x90\x00\x90\x90\x55\x90\x90\xaa\x90\x90\xff\x90\xb4\x00\x90\xb4\x55\x90\xb4\xaa\x90\xb4\xff\x90\xd8\x00\x90\xd8\x55\x90\xd8\xaa\x90\xd8\xff\x90\xfc\x00\x90\xfc\x55\x90\xfc\xaa\x90\xfc\xff\xb4\x00\x00\xb4\x00\x55\xb4\x00\xaa\xb4\x00\xff\xb4\x24\x00\xb4\x24\x55\xb4\x24\xaa\xb4\x24\xff\xb4\x48\x00\xb4\x48\x55\xb4\x48\xaa\xb4\x48\xff\xb4\x6c\x00\xb4\x6c\x55\xb4\x6c\xaa\xb4\x6c\xff\xb4\x90\x00\xb4\x90\x55\xb4\x90\xaa\xb4\x90\xff\xb4\xb4\x00\xb4\xb4\x55\xb4\xb4\xaa\xb4\xb4\xff\xb4\xd8\x00\xb4\xd8\x55\xb4\xd8\xaa\xb4\xd8\xff\xb4\xfc\x00\xb4\xfc\x55\xb4\xfc\xaa\xb4\xfc\xff\xd8\x00\x00\xd8\x00\x55\xd8\x00\xaa\xd8\x00\xff\xd8\x24\x00\xd8\x24\x55\xd8\x24\xaa\xd8\x24\xff\xd8\x48\x00\xd8\x48\x55\xd8\x48\xaa\xd8\x48\xff\xd8\x6c\x00\xd8\x6c\x55\xd8\x6c\xaa\xd8\x6c\xff\xd8\x90\x00\xd8\x90\x55\xd8\x90\xaa\xd8\x90\xff\xd8\xb4\x00\xd8\xb4\x55\xd8\xb4\xaa\xd8\xb4\xff\xd8\xd8\x00\xd8\xd8\x55\xd8\xd8\xaa\xd8\xd8\xff\xd8\xfc\x00\xd8\xfc\x55\xd8\xfc\xaa\xd8\xfc\xff\xfc\x00\x00\xfc\x00\x55\xfc\x00\xaa\xfc\x00\xff\xfc\x24\x00\xfc\x24\x55\xfc\x24\xaa\xfc\x24\xff\xfc\x48\x00\xfc\x48\x55\xfc\x48\xaa\xfc\x48\xff\xfc\x6c\x00\xfc\x6c\x55\xfc\x6c\xaa\xfc\x6c\xff\xfc\x90\x00\xfc\x90\x55\xfc\x90\xaa\xfc\x90\xff\xfc\xb4\x00\xfc\xb4\x55\xfc\xb4\xaa\xfc\xb4\xff\xfc\xd8\x00\xfc\xd8\x55\xfc\xd8\xaa\xfc\xd8\xff\xfc\xfc\x00\xfc\xfc\x55\xfc\xfc\xaa\xfc\xfc\xff"

def imgto332(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    palette = Image.new("P", (1, 1))
    palette.putpalette(RGB332)
    newimage = image.quantize(palette=palette, dither=Image.FLOYDSTEINBERG)
    data = []
    for i in range(0, newimage.width * newimage.height, 1):
        data.append(newimage.tobytes()[i])
    return data

def imgto565(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    data = []
    size = image.width*image.height*3
    idata = image.tobytes()
    for i in range(0, size, 3):
        r = idata[i]
        g = idata[i+1]
        b = idata[i+2]
        data.append((r>>3<<11)|(g>>2<<5)|(b>>3))
    return data

def imgto666(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    data = []
    size = image.width*image.height*3
    idata = image.tobytes()
    for i in range(0, size, 3):
        r = idata[i]
        g = idata[i+1]
        b = idata[i+2]
        data.append((r>>2<<26)|(g>>2<<20)|(b>>2<<14))
    return data

def imgto888(image):
    if image.mode != "RGB":
        image = image.convert("RGB")

    data = []
    size = image.width*image.height*3
    idata = image.tobytes()
    for i in range(0, size, 3):
        r = idata[i]
        g = idata[i+1]
        b = idata[i+2]
        data.append((r<<16)|(g<<8)|(b))
    return data

def imgto8888(image):
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    data = []
    size = image.width*image.height*4
    idata = image.tobytes()
    for i in range(0, size, 4):
        r = idata[i]
        g = idata[i+1]
        b = idata[i+2]
        a = idata[i+3]
        data.append(((0xff-a)<<24)|(r<<16)|(g<<8)|b)
    return data

def quantizetopalette(silf, palette, dither=False):
    """Convert an RGB or L mode image to use a given P image's palette."""

    silf.load()

    palette.load()
    if palette.mode != "P":
        raise ValueError("bad mode for palette image")
    if silf.mode != "RGB" and silf.mode != "L":
        raise ValueError(
            "only RGB or L mode images can be quantized to a palette"
            )
    im = silf.im.convert("P", 1 if dither else 0, palette.im)

    try:
        return silf._new(im)
    except AttributeError:
        return silf._makeself(im)

prev_buffer_xor = None

def encode_1bpp_2bpp(image, bpp, invert = False, xor_frame = False):
    global prev_buffer_xor
   
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    if bpp == 1:
        palette = Image.new("P", (1, 1))
        palette.putpalette([0, 0, 0, 255, 255, 255])
    elif bpp == 2:
        palette = Image.new("P", (1, 1))
        palette.putpalette([0, 0, 0, 96, 96, 96, 192, 192, 192, 255, 255, 255])

    newimage = image.quantize(palette=palette, dither=Image.FLOYDSTEINBERG).convert('L')

    img_data = bytearray(newimage.tobytes())

    a = 0
    for a in range(len(img_data)):
        if bpp == 1:
            img_data[a] = img_data[a] >> 7
            if invert:
                img_data[a] = 1 - img_data[a]
        elif bpp == 2:
            img_data[a] = img_data[a] >> 6
            if invert:
                img_data[a] = 3 - img_data[a]

    temp_data = []
    if xor_frame and prev_buffer_xor:
        for a in range(len(img_data)):
            temp_data.append(prev_buffer_xor[a] ^ img_data[a])
    else:
        for a in range(len(img_data)):
            temp_data.append(img_data[a])

    img_out = bytearray()

    max_rle_medium = 2048
    max_rle_short = 16
    if bpp == 1:
        twostep_pels = 14
        onestep_pels = 6
        rle_long_shift = 15
        rle_med_shift = 7
        two_step_rle_compens_len = 8
    elif bpp == 2:
        twostep_pels = 7
        onestep_pels = 3
        rle_long_shift = 14
        rle_med_shift = 6
        two_step_rle_compens_len = 3
    

    b = 0
    while b < len(temp_data):
        pixel = temp_data[b]
        count = 0
        while b + count < len(temp_data) and temp_data[b + count] == pixel:
            count += 1

        if count > 1:
            if count >= max_rle_medium:
                temp = (count & ((1 << rle_long_shift) - 1)) << bpp | pixel
                cmd = (count >> rle_long_shift) | 0x60
                img_out.append(cmd)
                img_out.append((temp >> 8) & 0xff)
                img_out.append(temp & 0xff)
            elif count >= max_rle_short:
                temp = (count & ((1 << rle_med_shift) - 1)) << bpp | pixel
                cmd = (count >> rle_med_shift) | 0x40
                img_out.append(cmd)
                img_out.append(temp & 0xff)
            else:
                cmd = (count << bpp) | pixel
                img_out.append(cmd)
            b += count
        else:
            lit_pels = []
            while b < len(temp_data) and len(lit_pels) < twostep_pels:
                p_pixel = temp_data[b]
                p_run = 0
                while b + p_run < len(temp_data) and temp_data[b + p_run] == p_pixel:
                    p_run += 1
                
                if p_run >= twostep_pels:
                    target = onestep_pels if len(lit_pels) < onestep_pels else twostep_pels
                    take = max(0, target - len(lit_pels))
                    take = min(take, p_run) 
                    
                    lit_pels.extend([temp_data[b]] * take)
                    b += take
                    break 
                else:
                    take = min(p_run, twostep_pels - len(lit_pels))
                    lit_pels.extend([temp_data[b]] * take)
                    b += take           

            #In original encoder and some research, it was found out
            #that the second half of the step (if two step) must be
            #checked to see if it is a whole run, if so we set a flag
            #to encode it into one step and decrement the offset
            #to encode it from that second half
            if bpp == 1:
                len_arr = [1]
            elif bpp == 2:
                len_arr = [1,2]
            if len(lit_pels) == twostep_pels:
                compensation = lit_pels[onestep_pels:]
                runs = []
                my_run = 1
                for _ in range(two_step_rle_compens_len-1):
                    if compensation[_+1] == compensation[_]:
                        my_run += 1
                    else:
                        runs.append(my_run)
                        my_run = 0
                    if _ == two_step_rle_compens_len-2:
                        runs.append(my_run)
                        break
                if len(runs) == 1:
                    #we found a run block, let's make it a one step
                    b -= len(compensation)
                    lit_pels = lit_pels[:onestep_pels]


            is_twostep = len(lit_pels) == twostep_pels
            target = twostep_pels if is_twostep else onestep_pels

            temp = 0
            for p in lit_pels:
                temp = (temp << bpp) | p
                
            if not is_twostep:
                img_out.append(temp | 0x80)

            else:
                img_out.append((temp >> 8) | 0xc0)
                img_out.append(temp & 0xff)

    if prev_buffer_xor is None:
        prev_buffer_xor = []
        for b in range(len(img_data)):
            prev_buffer_xor.append(img_data[b])
    else:
        for b in range(len(img_data)):
            prev_buffer_xor[b] = img_data[b]

    return img_out

def encode_8bpp_up(image, bpp, xor_frame = False):
    global prev_buffer_xor
    
    if bpp == 8:
        img_data = imgto332(image)
    elif bpp == 16:
        img_data = imgto565(image)
    elif bpp == 24:
        img_data = imgto888(image)
    elif bpp == 32:
        img_data = imgto8888(image)
    elif bpp == 18:
        img_data = imgto666(image)
        bpp = 32
    
    temp_data = []
    if xor_frame and prev_buffer_xor:
        for a in range(len(img_data)):
            temp_data.append(prev_buffer_xor[a] ^ img_data[a])
    else:
        for a in range(len(img_data)):
            temp_data.append(img_data[a])

    b = 0
    img_out = bytearray()

    while b < len(temp_data):
        pixel = temp_data[b]
        b += 1
        count = 1

        while (b < len(temp_data)) and (temp_data[b] == pixel):
            b += 1
            count += 1

        if pixel&0xff >= 0xc0 and count == 1:
            cmd = 0xc1
            img_out.append(cmd)
        elif count > 1:
            if count < 32:
                img_out.append(0xc0 + count)
            elif count < 4096:
                cmd = 0xe0 | count >> 8
                img_out.append(cmd)
                img_out.append(count & 0xff)
            else:
                cmd = 0xf0 | count >> 16
                img_out.append(cmd)
                img_out.append(count >> 8 & 0xff)
                img_out.append(count & 0xff)

        if bpp == 8:
            img_out.append(pixel)
        elif bpp == 16:
            img_out.append(pixel & 0xff)
            img_out.append(pixel >> 8)
        elif bpp == 24:
            img_out.append(pixel & 0xff)
            img_out.append((pixel >> 8) & 0xff)
            img_out.append(pixel >> 16)
        elif bpp == 32:
            img_out.append(pixel & 0xff)
            img_out.append((pixel >> 8) & 0xff)
            img_out.append((pixel >> 16) & 0xff)
            img_out.append(pixel >> 24)

    if prev_buffer_xor is None:
        prev_buffer_xor = []
        for b in range(len(img_data)):
            prev_buffer_xor.append(img_data[b])
    else:
        for b in range(len(img_data)):
            prev_buffer_xor[b] = img_data[b]

    return img_out

if __name__ == "__main__":
    ap = argparse.ArgumentParser("img2pdk")
    
    ap.add_argument("--version", "-v", help="PAF version to use", default=1, type=int, choices=[1, 2, 3])
    ap.add_argument("--bpp", "-b", help="Bits per pixel", default=8, type=int, choices=[1, 2, 8, 16, 18, 24, 32])
    ap.add_argument("--invert", "-i", help="Invert colors (useful only in 1bpp or 2bpp)", action="store_true")
    ap.add_argument("out_file")
    ap.add_argument("in_files", nargs="*")

    args = ap.parse_args()

    version = args.version
    bpp = args.bpp
    invert = args.invert
    out_file = args.out_file
    in_files = args.in_files

    f = open(out_file, "wb")

    img_array = []
    enc_image_array = []
    img_cnt = 0
    hdr_offset = 0
    img_width = 0
    img_height = 0

    header = bytearray()

    # encode
    for in_file in in_files:
        if img_cnt == 0:
            image = Image.open(in_file)
            img_width = image.width
            img_height = image.height
            img_cnt += 1
            img_array.append(image)
        else:
            image = Image.open(in_file)
            if (image.width != img_width) or (image.height != img_height):
                raise ValueError("All images must have the same dimensions")
            img_cnt += 1
            img_array.append(image)

    if args.version == 1:
        f.write(b"PAF1" + struct.pack("<BBBB", bpp, img_width, img_height, img_cnt))
        
    elif args.version == 2:
        f.write(b"PAF2" + struct.pack("<LLLL", bpp, img_width, img_height, img_cnt))
        
    elif args.version == 3:
        f.write(b"PAF3" + struct.pack("<BLLB", bpp, img_width, img_height, img_cnt))
        
    hdr_offset = f.tell() + 4*(img_cnt+1)
    
    enc_img_cnt = 0

    for img in img_array:
        if bpp >= 8:
            if enc_img_cnt > 0:
                enc_image_array.append(encode_8bpp_up(img, bpp, True))
            else:
                enc_image_array.append(encode_8bpp_up(img, bpp, False))
        else:
            if enc_img_cnt > 0:
                enc_image_array.append(encode_1bpp_2bpp(img, bpp, invert, True))
            else:
                enc_image_array.append(encode_1bpp_2bpp(img, bpp, invert, False))
        enc_img_cnt += 1

    enc_image_array.append(b"EndOfPAF\0")
    
    for i in range(img_cnt + 1):
        f.write(hdr_offset.to_bytes(4, "big"))
        hdr_offset += len(enc_image_array[i])
    
    for img in enc_image_array:
        f.write(img)

    f.close()
