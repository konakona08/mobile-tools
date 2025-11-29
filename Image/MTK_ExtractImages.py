import os, sys
import struct
from PIL import Image
from apng import APNG, PNG
from io import BytesIO
from abm import ab1Decode, ab2Decode
#plutommi\Framework\GDI\GDIInc\gdi_const.h

GDI_IMAGE_TYPE_INVALID                 = 0
GDI_IMAGE_TYPE_BMP                     = 1
GDI_IMAGE_TYPE_BMP_SEQUENCE            = 2
GDI_IMAGE_TYPE_GIF                     = 3
GDI_IMAGE_TYPE_DEVICE_BITMAP           = 4
GDI_IMAGE_TYPE_DEVICE_BITMAP_SEQUENCE  = 5
GDI_IMAGE_TYPE_BMP_FILE                = 6
GDI_IMAGE_TYPE_GIF_FILE                = 7
GDI_IMAGE_TYPE_WBMP_FILE               = 8
GDI_IMAGE_TYPE_JPG                     = 9
GDI_IMAGE_TYPE_JPG_FILE                = 10
GDI_IMAGE_TYPE_WBMP                    = 11
GDI_IMAGE_TYPE_AVI                     = 12
GDI_IMAGE_TYPE_AVI_FILE                = 13
GDI_IMAGE_TYPE_3GP                     = 14
GDI_IMAGE_TYPE_3GP_FILE                = 15
GDI_IMAGE_TYPE_MP4                     = 16
GDI_IMAGE_TYPE_MP4_FILE                = 17
GDI_IMAGE_TYPE_JPG_SEQUENCE            = 18
GDI_IMAGE_TYPE_PNG                     = 19
GDI_IMAGE_TYPE_PNG_FILE                = 20
GDI_IMAGE_TYPE_PNG_SEQUENCE            = 21
GDI_IMAGE_TYPE_DEVICE_BMP_FILE         = 22
GDI_IMAGE_TYPE_BMP_FILE_OFFSET         = 23
GDI_IMAGE_TYPE_GIF_FILE_OFFSET         = 24
GDI_IMAGE_TYPE_M3D                     = 25
GDI_IMAGE_TYPE_M3D_FILE                = 26
GDI_IMAGE_TYPE_SVG                     = 27
GDI_IMAGE_TYPE_SVG_FILE                = 28
GDI_IMAGE_TYPE_SWFLASH                 = 29
GDI_IMAGE_TYPE_SWFLASH_FILE            = 30

GDI_IMAGE_TYPE_JPG_FILE_OFFSET         = 31
GDI_IMAGE_TYPE_PNG_FILE_OFFSET         = 32
GDI_IMAGE_TYPE_DEVICE_BMP_FILE_OFFSET  = 33
GDI_IMAGE_TYPE_WBMP_FILE_OFFSET        = 34
GDI_IMAGE_TYPE_M3D_FILE_OFFSET         = 35
GDI_IMAGE_TYPE_SVG_FILE_OFFSET         = 36
GDI_IMAGE_TYPE_SWFLASH_FILE_OFFSET     = 37
GDI_IMAGE_TYPE_AVATAR                  = 38

GDI_IMAGE_TYPE_ABM_FILE_OFFSET         = 39
GDI_IMAGE_TYPE_ABM                     = 40
GDI_IMAGE_TYPE_ABM_SEQUENCE            = 41
GDI_IMAGE_TYPE_ABM_FILE                = 42

GDI_IMAGE_TYPE_MPG                     = 43
GDI_IMAGE_TYPE_MPG_FILE                = 44
GDI_IMAGE_TYPE_MPG_FILE_OFFSET         = 45

GDI_IMAGE_TYPE_3G2                     = 46
GDI_IMAGE_TYPE_3G2_FILE                = 47
GDI_IMAGE_TYPE_3G2_FILE_OFFSET         = 48

GDI_IMAGE_TYPE_VIS                     = 49
GDI_IMAGE_TYPE_VIS_FILE                = 50

GDI_IMAGE_TYPE_BMP_MEM                 = 51

GDI_IMAGE_TYPE_AB2                     = 52
GDI_IMAGE_TYPE_AB2_SEQUENCE            = 53
GDI_IMAGE_TYPE_AB2_FILE                = 54
GDI_IMAGE_TYPE_AB2_FILE_OFFSET         = 55

GDI_IMAGE_TYPE_BMP_SEQUENCE_FILE_OFFSET  = 56
GDI_IMAGE_TYPE_DEVICE_BITMAP_SEQUENCE_FILE_OFFSET  = 57
GDI_IMAGE_TYPE_JPG_SEQUENCE_FILE_OFFSET  = 58
GDI_IMAGE_TYPE_PNG_SEQUENCE_FILE_OFFSET  = 59
GDI_IMAGE_TYPE_ABM_SEQUENCE_FILE_OFFSET  = 60
GDI_IMAGE_TYPE_AB2_SEQUENCE_FILE_OFFSET  = 61

GDI_IMAGE_TYPE_9SLICE                  = 62
GDI_IMAGE_TYPE_9SLICE_FILE             = 63
GDI_IMAGE_TYPE_9SLICE_FILE_OFFSET      = 64

GDI_IMAGE_TYPE_RM_FILE                 = 65
GDI_IMAGE_TYPE_RA_FILE                 = 66

GDI_IMAGE_TYPE_KTX                     = 67
GDI_IMAGE_TYPE_KTX_FILE                = 68

GDI_IMAGE_TYPE_MAV                     = 69
GDI_IMAGE_TYPE_MAV_FILE                = 70

GDI_IMAGE_TYPE_SUM                     = 71
GDI_IMAGE_TYPE_DEV_BMP                 = 80

GDI_ERROR_HANDLE                       = (0)
GDI_NULL_HANDLE                        = (0)

if __name__ == "__main__":
    sz = os.path.getsize(sys.argv[1])
    fd = open(sys.argv[1], "rb")
    #####argv2 is align
    align = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    a = 0
    szt = 0
    while sz > 0:
        img_type, img_frames, img_size1, img_size2, img_size3, img_wh1, img_wh2, img_wh3 = struct.unpack("<BBBBBBBB", fd.read(8))
        img_size = img_size1 | (img_size2 << 8) | (img_size3 << 16)
        img_width = img_wh1 | ((img_wh2&0xf) << 8)
        img_height = (img_wh2>>4) | (img_wh3 << 4)
        sz -= 8
        if img_type == GDI_IMAGE_TYPE_BMP or img_type == GDI_IMAGE_TYPE_BMP_FILE:
            ext = "bmp"
        elif img_type == GDI_IMAGE_TYPE_JPG or img_type == GDI_IMAGE_TYPE_JPG_FILE:
            ext = "jpg"
        elif img_type == GDI_IMAGE_TYPE_PNG or img_type == GDI_IMAGE_TYPE_PNG_FILE:
            ext = "png"
        elif img_type == GDI_IMAGE_TYPE_GIF or img_type == GDI_IMAGE_TYPE_GIF_FILE:
            ext = "gif"
        elif img_type == GDI_IMAGE_TYPE_ABM or img_type == GDI_IMAGE_TYPE_ABM_FILE:
            ext = "abm"
        elif img_type == GDI_IMAGE_TYPE_AB2 or img_type == GDI_IMAGE_TYPE_AB2_FILE:
            ext = "ab2"
        elif img_type == GDI_IMAGE_TYPE_9SLICE or img_type == GDI_IMAGE_TYPE_9SLICE_FILE:
            ext = "9slice"
        elif img_type == GDI_IMAGE_TYPE_RM_FILE:
            ext = "rm"
        elif img_type == GDI_IMAGE_TYPE_RA_FILE:
            ext = "ra"
        elif img_type == GDI_IMAGE_TYPE_KTX or img_type == GDI_IMAGE_TYPE_KTX_FILE:
            ext = "ktx"
        elif img_type == GDI_IMAGE_TYPE_MAV or img_type == GDI_IMAGE_TYPE_MAV_FILE:
            ext = "mav"
        elif img_type == GDI_IMAGE_TYPE_SUM:
            ext = "sum"
        else:
            ext = "bin"
        
        print(ext, fd.tell())
        
        os.makedirs(f"{sys.argv[1]}_ext", exist_ok=True)
        print(img_type)
        if img_type == GDI_IMAGE_TYPE_PNG_SEQUENCE or img_type == GDI_IMAGE_TYPE_BMP_SEQUENCE:
            frame_info = []
            frame_data = []
            for i in range(img_frames):
                frame_info.append(struct.unpack("<LLL", fd.read(12)))
                print(frame_info[i])
                sz -= 12
                szt += 12
            for i in range(img_frames):
                img_data = fd.read(frame_info[i][1])
                frame_data.append(img_data)
                sz -= frame_info[i][1]
                szt += frame_info[i][1]
                if szt % align != 0:
                    t = (align - (szt % align))
                    fd.read(t)
                    szt += t
                    sz-=(t)
            
            #########temp create
            temp_png_paths = []
            for i, png_bytes in enumerate(frame_data):
                temp_path = f"{sys.argv[1]}_ext/temp_frame_{i}.{ext}"
                with open(temp_path, "wb") as f:
                    f.write(png_bytes)
                temp_png_paths.append(temp_path)

            APNG.from_files(temp_png_paths, delay=frame_info[i][2]).save(f"{sys.argv[1]}_ext/{a}.png")

            # Clean up temporary files (optional)
            import os
            for p in temp_png_paths:
                os.remove(p)
        elif img_type == GDI_IMAGE_TYPE_ABM_SEQUENCE:
            frame_info = []
            frame_data = []
            for i in range(img_frames):
                frame_info.append(struct.unpack("<LLL", fd.read(12)))
                print(frame_info[i])
                sz -= 12
                szt += 12
            for i in range(img_frames):
                img_data = fd.read(frame_info[i][1])
                frame_data.append(img_data)
                sz -= frame_info[i][1]
                szt += frame_info[i][1]
                if szt % align != 0:
                    t = (align - (szt % align))
                    fd.read(t)
                    szt += t
                    sz-=(t)
        else:
            img_data = fd.read(img_size)
            #####debug
            if img_type == GDI_IMAGE_TYPE_ABM:
                conv = ab1Decode(img_data)
                conv.save(f"{sys.argv[1]}_ext/{a}.png")
            elif img_type == GDI_IMAGE_TYPE_AB2:
                conv = ab2Decode(img_data)
                conv.save(f"{sys.argv[1]}_ext/{a}.png")
            else:
                open(f"{sys.argv[1]}_ext/{a}.{ext}", "wb").write(img_data)
        sz -= img_size
        a+=1
        szt += img_size+8
        ####set align to 1 if bmp or bmpsequence:
        type = fd.read(1)[0]
        fd.seek(fd.tell()-1)
        print("aign tell:", type, fd.tell())
        if type == GDI_IMAGE_TYPE_BMP or type == GDI_IMAGE_TYPE_BMP_SEQUENCE:
            align = 1
        elif type == GDI_IMAGE_TYPE_INVALID:
            print("aigning ", szt)
            align = 4
            ####align to 4 bytes
            if szt % align != 0:
                t = (align - (szt % align))
                fd.read(t)
                szt += t
                sz-=(t)