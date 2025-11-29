from PIL import Image
import FindArch
import ctypes
import os
import typing
from enum import IntEnum
import argparse

#############types
class libwica_csp(IntEnum):
    AUTO = 0
    USER = (1 << 0) #4:2:0 planar  = (1<<(==I420, except for pointers/strides)
    I420 = (1 << 1) #4:2:0 planar
    YV12 = (1 << 2) #4:2:0 planar
    YV24 = (1 << 3) #4:4:4 planar
    YUY2 = (1 << 4) #4:2:2 packed
    UYVY = (1 << 5) #4:2:2 packed
    YVYU = (1 << 6) #4:2:2 packed
    BGRA = (1 << 7) #32-bit BGRA packed
    ABGR = (1 << 8) #32-bit ABGR packed
    RGBA = (1 << 9) #32-bit RGBA packed
    ARGB = (1 << 10) #32-bit ARGB packed
    BGR = (1 << 11) #24-bit BGR packed
    RGB = (1 << 12) #24-bit RGB packed
    RGB555 = (1 << 13) #15-bit RGB555 packed into 16 bit
    RGB565 = (1 << 14) #16-bit RGB565 packed into 16 bit
    RGB666 = (1 << 15) #18-bit RGB666 packed into 24 bit
    GRAYSCALE = (1 << 16) #only luma component
    RGB56588 = (1 << 17) #16-bit RGB565 and alpha channel packed into 32 bit
    RGB6668 = (1 << 18) #18-bit RGB666 and alpha channel packed into 32 bit
    YV12A = (1 << 23) #4:2:0 planar with alpha channel
    YV24A = (1 << 24) #4:4:4 planar with alpha channel
    VFLIP = (1 << 30) #vertical flip mask

    @classmethod
    def from_param(cls, obj):
        return int(obj)

class libwica_io_type(IntEnum):
    FILE = 0
    MEMORY = 1

    @classmethod
    def from_param(cls, obj):
        return int(obj)

class libwica_decode_speed(IntEnum):
    NORMAL = 0
    FAST = 1
    MAX = 2

    @classmethod
    def from_param(cls, obj):
        return int(obj)

##stream

class libwica_stream(ctypes.Structure):
    _fields_ = [
        ("pbtData", ctypes.c_void_p),
        ("iLength", ctypes.c_int),
        ("iOffset", ctypes.c_int)
    ]

###determine os first
os_bits = FindArch.get_platform()

file_to_load = "libwica" + str(os_bits) + ".dll"

try:
    a = ctypes.CDLL(os.path.join(os.path.dirname(__file__), file_to_load))
except Exception:
    print("Failed to load library")
    exit(1)

# WcaLib_Handle WcaLib_Create(void* pData, int nSize, WcaLib_IOType eType)
libwica_handle_create = a.WcaLib_Create
libwica_handle_create.argtypes = [ctypes.c_void_p, ctypes.c_int, libwica_io_type]
libwica_handle_create.restype = ctypes.c_void_p

# bool WcaLib_SetDecoderCSP(WcaLib_Handle pHandle, WcaLib_CSP eCSP)
libwica_set_decoder_csp = a.WcaLib_SetDecoderCSP
libwica_set_decoder_csp.argtypes = [ctypes.c_void_p, libwica_csp]
libwica_set_decoder_csp.restype = ctypes.c_bool

# bool WcaLib_Decode(WcaLib_Handle pHandle, int nFrame, int* pnDelay)
libwica_decode = a.WcaLib_Decode
libwica_decode.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
libwica_decode.restype = ctypes.c_bool

# unsigned char* WcaLib_GrabImage(WcaLib_Handle pHandle)
libwica_grab_image = a.WcaLib_GrabImage
libwica_grab_image.argtypes = [ctypes.c_void_p]
libwica_grab_image.restype = ctypes.c_void_p

# bool WcaLib_GrabDimensions(WcaLib_Handle pHandle, int* pnWidth, int* pnHeight, int* pnBitsPerPixel)
libwica_grab_dimensions = a.WcaLib_GrabDimensions
libwica_grab_dimensions.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
libwica_grab_dimensions.restype = ctypes.c_bool

# bool WcaLib_GrabFrames(WcaLib_Handle pHandle, int* pnFrames, int* pnFps)
libwica_grab_frames = a.WcaLib_GrabFrames
libwica_grab_frames.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
libwica_grab_frames.restype = ctypes.c_bool

# void WcaLib_Destroy(WcaLib_Handle pHandle)
libwica_destroy = a.WcaLib_Destroy
libwica_destroy.argtypes = [ctypes.c_void_p]
libwica_destroy.restype = None

############################# encoder

# WcaLib_Handle WcaLib_EncoderCreate(int nWidth, int nHeight, int nFrames)

libwica_encoder_create = a.WcaLib_EncoderCreate
libwica_encoder_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
libwica_encoder_create.restype = ctypes.c_void_p

# bool WcaLib_WriteImage(WcaLib_Handle pHandle, char* pImage, WcaLib_CSP eCSP)

libwica_write_image = a.WcaLib_WriteImage
libwica_write_image.argtypes = [ctypes.c_void_p, ctypes.c_void_p, libwica_csp]
libwica_write_image.restype = ctypes.c_bool

# bool WcaLib_SetEncodeParam(WcaLib_Handle pHandle, WcaLib_CSP eCSP, WcaLib_DecodeSpeed eDecSpeed, int iQuality)

libwica_set_encode_param = a.WcaLib_SetEncodeParam
libwica_set_encode_param.argtypes = [ctypes.c_void_p, libwica_csp, libwica_decode_speed, ctypes.c_int]
libwica_set_encode_param.restype = ctypes.c_bool

# bool WcaLib_EncodeNewFrame(WcaLib_Handle pHandle)
libwica_encode_new_frame = a.WcaLib_EncodeNewFrame
libwica_encode_new_frame.argtypes = [ctypes.c_void_p]
libwica_encode_new_frame.restype = ctypes.c_bool

# void WcaLib_GetEncodedData(WcaLib_Handle pHandle, unsigned char** ppbtData, int* piLength)

libwica_get_encoded_data = a.WcaLib_GetEncodedData
libwica_get_encoded_data.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_int)]
libwica_get_encoded_data.restype = None

# bool WcaLib_EncoderAssemble(WcaLib_Handle pHandle, int iFPS)

libwica_encoder_assemble = a.WcaLib_EncoderAssemble
libwica_encoder_assemble.argtypes = [ctypes.c_void_p, ctypes.c_int]
libwica_encoder_assemble.restype = ctypes.c_bool

# WcaLib_Stream* WcaLib_GetAssembledData(WcaLib_Handle pHandle)

libwica_get_assembled_data = a.WcaLib_GetAssembledData
libwica_get_assembled_data.argtypes = [ctypes.c_void_p]
libwica_get_assembled_data.restype = ctypes.c_void_p

# bool WcaLib_RemoveFrame(WcaLib_Handle pHandle)

libwica_remove_frame = a.WcaLib_RemoveFrame
libwica_remove_frame.argtypes = [ctypes.c_void_p]
libwica_remove_frame.restype = ctypes.c_bool

# void WcaLib_EncoderDestroy(WcaLib_Handle pHandle)

libwica_encoder_destroy = a.WcaLib_EncoderDestroy
libwica_encoder_destroy.argtypes = [ctypes.c_void_p]
libwica_encoder_destroy.restype = None

def ptr_to_byte(ptr, size):
    data = ctypes.cast(ptr, ctypes.POINTER(ctypes.c_ubyte))
    return bytearray(data[:size])

def bgra_to_rgba(data):
    for i in range(0, len(data), 4):
        t = data[i]
        data[i] = data[i+2]
        data[i+2] = t
    return data

def fix_alpha(data):
    for i in range(0, len(data), 4):
        data[i+3] = 0xFF
    return data

class Wica:
    def __init__(self):
        self._handle = None
        self._width = ctypes.c_int()
        self._height = ctypes.c_int()
        self._frames = ctypes.c_int()
        self._fps = ctypes.c_int()
        self._bpp = ctypes.c_int()
        self._frame_delay = ctypes.c_int()
        self._csp = libwica_csp.BGRA
        self._imgdata = None
        self._fake_alpha = False
        self._curframe = 0
        self._is_encoder = False
    def encode(self, images: [], quality: int, fps: int):
        ###check w and h of every image
        if len(images) == 0:
            return None
        w = images[0].width
        h = images[0].height
        for image in images:
            if image.width != w or image.height != h:
                return None
        self._handle = libwica_encoder_create(w, h, len(images))
        if self._handle == 0:
            print("Failed to create encoder")
            exit(1)
        print(f"enc addr {self._handle} info: {w}x{h} {len(images)} frames {fps} fps {quality} quality")
        ret = libwica_set_encode_param(self._handle, self._csp, libwica_decode_speed.NORMAL, quality)
        if not ret:
            print("Failed to set encode param")
            exit(1)
        for image in images:
            idata = bytearray(image.tobytes())
            self._imgdata = bgra_to_rgba(idata)
            ######convert to bytes back
            self._imgdata = bytes(self._imgdata)
            ret = libwica_write_image(self._handle, self._imgdata, self._csp)
            if not ret:
                print("Failed to write image")
                exit(1)
            ret = libwica_encode_new_frame(self._handle)
            if not ret:
                print("Failed to encode new frame")
                exit(1)
        ret = libwica_encoder_assemble(self._handle, fps)
        if not ret:
            print("Failed to assemble encoder")
            exit(1)
        stream = libwica_get_assembled_data(self._handle)
        ###cvt stream ptr to struct
        stream = ctypes.cast(stream, ctypes.POINTER(libwica_stream))
        self._is_encoder = True
        return ptr_to_byte(stream.contents.pbtData, stream.contents.iLength)
    def load(self, data: typing.Union[bytes, bytearray, str], fake_alpha = False):
        self._handle = libwica_handle_create(data, len(data), libwica_io_type.FILE if isinstance(data, str) else libwica_io_type.MEMORY)
        if self._handle == 0:
            print("Failed to load library")
            exit(1)
        result = libwica_set_decoder_csp(self._handle, self._csp)
        if not result:
            print("Failed to set decoder CSP")
            exit(1)
        result = libwica_grab_dimensions(self._handle, ctypes.byref(self._width), ctypes.byref(self._height), ctypes.byref(self._bpp))
        if not result:
            print("Failed to get dimensions")
            exit(1)
        result = libwica_grab_frames(self._handle, ctypes.byref(self._frames), ctypes.byref(self._fps))
        if not result:
            print("Failed to get frames")
            exit(1)
        self._fake_alpha = fake_alpha
        print(f"info: {self._width.value}x{self._height.value} {self._frames.value} frames {self._fps.value} fps {self._bpp.value} bpp")
        self._is_encoder = False
    def decode(self, frame: int):
        result = libwica_decode(self._handle, frame, ctypes.byref(self._frame_delay))
        if not result:
            print("Failed to decode frame")
            exit(1)
        self._imgdata = libwica_grab_image(self._handle)
        data = bgra_to_rgba(ptr_to_byte(self._imgdata, self._width.value * self._height.value * self._bpp.value // 8))
        if self._fake_alpha:
            data = fix_alpha(data)
        return Image.frombuffer("RGB", (self._width.value, self._height.value), data, "raw", "RGBA", 0, 1)
    def __iter__(self):
        self._curFrame = 0
        return self
    def __next__(self):
        if self._curFrame >= self._frames.value: raise StopIteration()
        frame = self.decode(self._curFrame)
        self._curFrame += 1
        return frame
    def destroy(self):
        if self._is_encoder:
            libwica_encoder_destroy(self._handle)
        else:
            libwica_destroy(self._handle)
        self._imgdata = None
        self._handle = None

if __name__ == "__main__":
    ap = argparse.ArgumentParser("wica")
    
    ap.add_argument("--fps", "-f", help="Frames per second", type=int, default=30)
    ap.add_argument("--quality", "-q", help="Quality of the encoded image", type=int, default=90)
    ap.add_argument("--decode", "-d", help="Decode WCI/WCA file", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--encode", "-e", help="Encode WCI/WCA file", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("--fakealpha", "-a", help="Add fake alpha channel (for some WCI/WCA images)", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("files", nargs='+', help="Input and output files")

    args = ap.parse_args()

    if args.decode == args.encode:
        ap.error("You must specify either --decode or --encode")

    wica = Wica()
    if args.encode:
        if len(args.files) < 2:
            ap.error("No in files and out file")
        in_files = args.files[:-1]
        out_file = args.files[-1]
        with open(out_file, "wb") as f:
            f.write(wica.encode([Image.open(in_file) for in_file in in_files], args.quality, args.fps))
    elif args.decode:
        if len(args.files) != 2:
            ap.error("No in file and out file")
        in_file = args.files[0]
        out_file = args.files[1]
        wica.load(open(in_file, "rb").read(), args.fakealpha)
        for frame in wica:
            frame.save(os.path.splitext(out_file)[0] + "_" + str(wica._curFrame) + os.path.splitext(out_file)[1])
    wica.destroy()
