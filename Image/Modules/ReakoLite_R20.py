
from __future__ import print_function
import sys
import os
import gc
import io
import typing
import struct
from PIL import Image

def _565to888(color_565):
    r = (color_565 >> 11) & 0x1F
    g = (color_565 >> 5) & 0x3F
    b = color_565 & 0x1F
    return (r << 3, g << 2, b << 3, 255)

class ReakoR20():
    def __init__(self, file: typing.Union[io.RawIOBase, bytearray, bytes, str]):
        self.__parsed = False
        dataIn = None
        if isinstance(file, bytes) or isinstance(file, bytearray):        
            dataIn = file
        elif isinstance(file, io.RawIOBase):
            dataIn = file.read()
        else:
            dataIn = open(file, "rb").read()
        assert dataIn[:0x3] == b'RL\x20', "Not a valid ReakoLite R20 image"
        assert len(dataIn) > 6, "ReakoLite R20 image incomplete: no data"
        dataIn = dataIn[0x3:]
        parsed = 0
        img_type = dataIn[parsed]
        parsed += 1
        assert img_type in [0x61, 0x6a], f"Not a valid ReakoLite R20 image type: {img_type}"

        self.frame_data = []

        if img_type == 0x6a:
            self.frames = 1
            self.frame_data.append(dataIn[parsed:]) 
        else:
            self.frames = struct.unpack("<H", dataIn[parsed:parsed+2])[0]
            parsed += 2
            for i in range(self.frames):
                frame_size = struct.unpack("<H", dataIn[parsed:parsed+2])[0]
                parsed += 2
                self.frame_data.append(dataIn[parsed:parsed+frame_size*2])
                parsed += frame_size*2

        self.change_color = struct.unpack("<H", self.frame_data[0][2:4])[0]
        po2w, po1h = struct.unpack("<HH", self.frame_data[0][4:8])
        self.width = po2w >> 6
        self.height = po1h >> 6

        self.img_out = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))

        self._curFrame = 0

        self.__parsed = True

    def decodeBlock(self, x, y, w, h):
        if len(self.__decode_commands):
            command = self.__decode_commands.pop(0)
            is_split = command & 1
            command >>= 1
            if is_split:
                mod_w = (command >> 1) & 0x3ff
                is_column = command & 1
                if is_column:
                    self.decodeBlock(x, y, mod_w, h)
                    self.decodeBlock(x + mod_w, y, w - mod_w, h)
                else:
                    self.decodeBlock(x, y, w, mod_w)
                    self.decodeBlock(x, y + mod_w, w, h - mod_w)
            else:
                temp_block = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                cols_used = command & 0xff
                bpp = ((command >> 8) & 0x7) + 1
                pal_manipulate = ((command >> 11) & 0x1) == 0
                self.__decode_palette_off = 0
                self.__decode_bitmap_off = 0
                pixel = self.change_color
                if cols_used == 0:
                    if ((pal_manipulate) or (self.replace_alpha == False)):
                        if (pal_manipulate):
                            pixel = self.__decode_palette[self.__decode_palette_off]
                        for i in range(h):
                            for j in range(w):
                                temp_block.putpixel((j, i), _565to888(pixel))
                else:
                    bit = 8
                    read_b_data = 0
                    if (pal_manipulate):
                        pixel = self.__decode_palette[self.__decode_palette_off]
                    else:
                        self.__decode_palette_off -= 1
                    read_b_data = self.__decode_bitmap[self.__decode_bitmap_off]
                    self.__decode_bitmap_off += 1
                    for i in range(h):
                        for j in range(w):
                            bit-=bpp
                            if (bit < 0):
                                bit += 8
                                read_b_data = (read_b_data<<8) | self.__decode_bitmap[self.__decode_bitmap_off]
                                self.__decode_bitmap_off += 1
                                
                            p_idx = (read_b_data >> bit) & (0xff >> (8 - bpp))
                            if p_idx:
                                temp_block.putpixel((j, i), _565to888(self.__decode_palette[self.__decode_palette_off+p_idx]))
                            elif ((pal_manipulate) or (self.replace_alpha == False)):
                                temp_block.putpixel((j, i), _565to888(pixel))
                    
                self.__decode_palette = self.__decode_palette[cols_used+(pal_manipulate):]
                self.__decode_bitmap = self.__decode_bitmap[self.__decode_bitmap_off:]
                self.img_out.paste(temp_block, (x, y))

    def get(self):
        if self._curFrame >= self.frames:
            return None

        attributes, change_color, po2w, po1h, bitmap_offset = struct.unpack("<HHHHH", self.frame_data[self._curFrame][:10])
        width = po2w >> 6
        height = po1h >> 6
        palette_offset = (po1h & 0x3F) | ((po2w << 6) & 0xFFF)
        
        idata = self.frame_data[self._curFrame][10:]

        self.__decode_commands = []
        self.__decode_palette = []

        self.__decode_commands_off = 0
        self.__decode_palette_off = 0
        self.__decode_bitmap_off = 0

        self.replace_alpha = False

        for i in range(palette_offset):
            self.__decode_commands.append(struct.unpack("<H", idata[i*2:i*2+2])[0])

        for i in range(bitmap_offset - palette_offset):
            self.__decode_palette.append(struct.unpack("<H", idata[(palette_offset + i)*2:(palette_offset + i)*2+2])[0])

        self.__decode_bitmap = idata[bitmap_offset * 2:]

        self.decodeBlock(0,0,width,height)
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