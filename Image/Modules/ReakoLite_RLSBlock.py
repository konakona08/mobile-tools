
from __future__ import print_function
import sys
import os
import gc
import io
import typing
import struct
from PIL import Image 

block_type_use_palette_bits = [ 8, 12, 12, 10, 9, 12, 10, 12, 13, 11, 14, 14, 14, 13, 15 ]

block_type_pixels = [[0,0,0,0],
					[0,1,1,1],
					[0,1,0,0], 
					[0,0,1,0],
					[0,0,0,1], 
					[0,1,0,1],
					[0,0,1,2], 
					[0,1,1,0],
					[0,1,0,2], 
					[0,0,1,2],
					[0,1,2,0], 
					[0,1,2,1],
					[0,1,2,2], 
					[0,1,1,2],
					[0,1,2,3]]

def _565to888(color_565):
    r = (color_565 >> 11) & 0x1F
    g = (color_565 >> 5) & 0x3F
    b = color_565 & 0x1F
    return (r << 3, g << 2, b << 3, 255)

class RLSBlock():
    def __init__(self, file: typing.Union[io.RawIOBase, bytearray, bytes, str]):
        self.__parsed = False
        dataIn = None
        if isinstance(file, bytes) or isinstance(file, bytearray):        
            dataIn = file
        elif isinstance(file, io.RawIOBase):
            dataIn = file.read()
        else:
            dataIn = open(file, "rb").read()
        assert dataIn[:0x3] in [b'RL\x10', b'RL\x13'], "Not a valid ReakoLite RLS (Block) image"
        assert len(dataIn) > 12, "ReakoLite RLS (Block) image incomplete: no data"
        type = dataIn[0x2]
        if type == 0x10:
            self.frames, self.width, self.height, _, _, self.w_odd, self.h_odd, _ = struct.unpack("<BBBBBBBB", dataIn[0x4:0xC])
        elif type == 0x13:
            self.frames, self.width, self.height, _, _, att = struct.unpack("<BHHBBB", dataIn[0x4:0xC])
            self.w_odd = att & 0x1
            self.h_odd = (att >> 1) & 0x1
        dataIn = dataIn[0xc:]

        self.frame_data = []

        parsed = 0

        for i in range(self.frames):
            prev_parsed = parsed
            parsed += 512
            ep_size = struct.unpack("<L", dataIn[parsed:parsed+4])[0]
            parsed += ep_size+4
            dat_size = struct.unpack("<L", dataIn[parsed:parsed+4])[0]
            parsed += dat_size+4
            self.frame_data.append(dataIn[prev_parsed:parsed])

        self.img_out = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        self._curFrame = 0

        self.__parsed = True

    def decodeBlock(self):
        block = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
        block_info = self.__decode_bitmap[self.__decode_parsed]
        self.__decode_parsed += 1
        use_palette_bits_item = block_info & 0xf
        use_mpalette_bits = block_info >> 4

        if use_palette_bits_item == 0xf:
            for i in range(2):
                for j in range(2):
                    not_use_alpha = not ((use_mpalette_bits >> (3 - ((i*2)+j))) & 1)
                    if not_use_alpha:
                        block.putpixel((j, i), _565to888(self.__decode_ext_palette.pop(0)))
        else:
            use_palette_bits = block_type_use_palette_bits[use_palette_bits_item]
            blk_col_array = block_type_pixels[use_palette_bits_item]
            for i in range(2):
                for j in range(2):
                    new = (use_palette_bits >> (3 - ((i*2)+j))) & 1
                    if not new:
                        pixel_in_block = blk_col_array[(i*2)+j]
                        p_x = pixel_in_block & 0x1
                        p_y = (pixel_in_block >> 1) & 0x1
                        pel = block.getpixel((p_x, p_y))
                    else:
                        std_pal = (use_mpalette_bits >> (3 - ((i*2)+j))) & 1
                        if std_pal:
                            pixel_offset = self.__decode_bitmap[self.__decode_parsed]
                            self.__decode_parsed += 1
                            pel = _565to888(self.__decode_palette[pixel_offset])
                        else:
                            pel = _565to888(self.__decode_ext_palette.pop(0))
                    block.putpixel((j, i), pel)
        return block
                            
    def decode(self):
        cols = (self.width+1) >> 1
        rows = (self.height+1) >> 1

        for i in range(rows):
            for j in range(cols):
                self.img_out.paste(self.decodeBlock(), (j*2, i*2))

    def get(self):
        if self._curFrame >= self.frames:
            return None

        self.__decode_commands = []
        self.__decode_palette = []
        self.__decode_ext_palette = []

        idata = self.frame_data[self._curFrame]

        for i in range(256):
            self.__decode_palette.append(struct.unpack("<H", idata[i*2:i*2+2])[0])

        parsed = 512

        epal_size = struct.unpack("<L", idata[parsed:parsed+4])[0]
        parsed += 4

        epal_data = idata[parsed:]
        parsed += epal_size

        epal_size = (epal_size+1)//2

        for i in range(epal_size):  
            try:
                self.__decode_ext_palette.append(struct.unpack("<H", epal_data[i*2:i*2+2])[0])
            except:
                pass

        dat_size = struct.unpack("<L", idata[parsed:parsed+4])[0]
        parsed += 4

        self.__decode_bitmap = idata[parsed:parsed+dat_size]

        self.__decode_parsed = 0
        self.__decode_epal_parsed = 256

        self.decode()
        self._curFrame += 1

        return self.img_out

    def __iter__(self):
        return self

    def __next__(self):
        frame = self.get()
        if not frame: raise StopIteration()
        return frame
                
    def __del__(self):
        if self.__parsed:
            gc.collect()    