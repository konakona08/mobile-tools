import sys
import io
import struct
import typing
import gc
from PIL import Image
import os

class SBA:
    def unpack_sba_packbits(self, data, size):
        result = bytearray()
        while data.tell() < size:
            pel = struct.unpack("<b", data.read(1))[0]
            if pel >= 0:
                to_copy = data.read(1)[0]
                for i in range(pel):
                    result.append(to_copy)
            else:
                for i in range(-pel):
                    result.append(data.read(1)[0])
        return result

    def unpack_sba_packbits565(self, data, size):
        result = bytearray()
        while data.tell() < size:
            pel = struct.unpack("<b", data.read(1))[0]
            if pel >= 0:
                to_copy = data.read(1)[0]
                to_copy2 = data.read(1)[0]
                for i in range(pel):
                    result.append(to_copy)
                    result.append(to_copy2)
            else:
                for i in range(-pel):
                    result.append(data.read(1)[0])
                    result.append(data.read(1)[0])
        return result

    def rgb444to888(self, cols):
        out = bytearray()
        for a in cols:
            r = (a>>8)&0xf
            g = (a>>4)&0xf
            b = (a)&0xf
            out.append(r<<4)
            out.append(g<<4)
            out.append(b<<4)
        return out

    def __init__(self, file: typing.Union[io.RawIOBase, bytearray, bytes, str]):
        self.__parsed = False
        self.__frames = []
        self.__w = 0
        self.__h = 0
        self.__frames_count = 0
        self.__speed = 0
        self.__palette = []
        self._curFrame = 0
        dataIn = None
        if isinstance(file, bytes) or isinstance(file, bytearray):        
            dataIn = file
        elif isinstance(file, io.RawIOBase):
            dataIn = file.read()
        else:
            dataIn = open(file, "rb").read()
        dataRead = io.BytesIO(dataIn)
        dataSize = len(dataIn)
        while dataRead.tell() < dataSize:
            magic = struct.unpack("<H", dataRead.read(2))[0]
            size = struct.unpack("<H", dataRead.read(2))[0]
            data = io.BytesIO(dataRead.read(size))
            if magic == 1:
                self.__w,self.__h,self.__frames_count = struct.unpack("<HHH", data.read(6))
            elif magic == 2:
                self.__speed = struct.unpack("<L", data.read(4))[0]
            elif magic == 6:
                p_size = size//2
                for i in range(p_size):
                    self.__palette.append(struct.unpack("<H", data.read(2))[0])
            elif magic == 7:
                self.__frames.append([self.unpack_sba_packbits(data, size), False])
            elif magic == 9:
                self.__frames.append([self.unpack_sba_packbits565(data, size), True])
        self.__parsed = True

    def get(self):
        if self._curFrame >= self.__frames_count:
            return None        

        fd = self.__frames[self._curFrame]

        if fd[1] == False:
            img = Image.new("P", (self.__w, self.__h))
            img.putdata(fd[0])
            img.putpalette(self.rgb444to888(self.__palette))
        else:
            img = Image.frombuffer("RGB", (self.__w, self.__h), fd[0], "raw", "BGR;16")

        self._curFrame += 1
        return img

    def __iter__(self):
        return self

    def __next__(self):
        frame = self.get()
        if not frame: raise StopIteration()
        return frame
                
    def __del__(self):
        if self.__parsed:
            gc.collect()    

    def get_speed(self):
        return self.__speed

if __name__ == "__main__":
    sba = SBA(sys.argv[1])
    if os.path.splitext(sys.argv[2])[1] != ".gif":
        for x, f in enumerate(sba):
            f.save(f"{os.path.splitext(sys.argv[2])[0]}_{x:04d}{os.path.splitext(sys.argv[2])[1]}")
    else:
        animation_frames = []
        for x, f in enumerate(sba):
            animation_frames.append(f)
        animation_frames[0].save(sys.argv[2], save_all=True, append_images=animation_frames[1:], duration=sba.get_speed(), loop=0)