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
		libwica_destroy(self._handle)
		self._imgdata = None
		self._handle = None

if __name__ == "__main__":
    ap = argparse.ArgumentParser("wica")
    
    ap.add_argument("--fakealpha", "-f", help="Add fake alpha channel (for some WCI/WCA images)", action=argparse.BooleanOptionalAction, default=False)
    ap.add_argument("in_file")
    ap.add_argument("out_file")

    args = ap.parse_args()

    wica = Wica()
    wica.load(open(args.in_file, "rb").read(), args.fakealpha)
    for frame in wica:
        frame.save(os.path.splitext(args.out_file)[0] + "_" + str(wica._curFrame) + os.path.splitext(args.out_file)[1])
    wica.destroy()
