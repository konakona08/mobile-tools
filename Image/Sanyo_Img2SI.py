from re import L
from PIL import Image
import os
import sys
import struct

def quant_to_241cols(image):
    if image.mode != "RGB" and image.mode != "RGBA":
        image = image.convert("RGB")

    quantized = image.quantize(colors=240, method=2, dither=Image.FLOYDSTEINBERG)
    palette = quantized.getpalette()

    palette_rgb = [tuple(palette[i:i+3]) for i in range(0, len(palette), 3)][:240]
    
    data = bytearray(quantized.tobytes())

    idx = -1
    for i in range(len(palette_rgb)):
        if palette_rgb[i] == (0xff, 0x00, 0xff):
            idx = i
            break
    
    if idx != -1:
        for i in range(len(data)):
            if data[i] == idx:
                data[i] = 0

    for i in range(len(data)):
        data[i] += 1

    new_palette = palette_rgb.copy()
    new_palette.insert(0, (0xff, 0x00, 0xff))

    return new_palette, quantized.width, quantized.height, data

def rle_encode_row(row):
    runs = []
    run = []
    a = 0
    while a < len(row):
        pixel = row[a]
        a += 1
        count = 1
        while a < len(row) and row[a] == pixel and count < 0xfe:
            a += 1
            count += 1
        run.append((count, pixel))
    runs.append(run)

    is_rle = False
    for run in runs:
        if run[0][0] > 1:
            is_rle = True
            break
    
    encoded = bytearray()
    if is_rle:
        encoded.append(0xff)
        for run in runs:
            for count, pixel in run:
                encoded.append(count)
                encoded.append(pixel)
    else:
        encoded.append(0x00)
        for pixel in row:
            encoded.append(pixel)
    return encoded

def rle_encode(image_data, w, h):
    encoded = bytearray()
    for a in range(h):
        row = image_data[a*w:(a+1)*w]
        encoded.extend(rle_encode_row(row))
    return encoded

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <input_image>")
        sys.exit(1)
    
    input_image = sys.argv[1]
    with Image.open(input_image) as img:
        palette_rgb, width, height, data = quant_to_241cols(img)
        with open(input_image + ".si", "wb") as f:
            f.write(b"SI\x10\x01")
            f.write(struct.pack("<H", 2))
            f.write(struct.pack("<H", width))
            f.write(struct.pack("<H", height))
            f.write(struct.pack("<H", 0))
            f.write(struct.pack("<B", 1))
            f.write(struct.pack("<B", len(palette_rgb)-1))
            f.write(struct.pack("<H", 2048))
            for color in palette_rgb:
                f.write(struct.pack("<H", (color[0]>>3<<11)|(color[1]>>2<<5)|(color[2]>>3)))
            f.write(rle_encode(data, width, height))


if __name__ == "__main__":
    main()