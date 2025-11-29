import struct
import lzma

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

IMAGE_HANDL_OFFSET_LENGTH = 5
IMAGE_GROUP_MASK = ( (0xFFFFFFFF >> (IMAGE_HANDL_OFFSET_LENGTH+1)) << (IMAGE_HANDL_OFFSET_LENGTH+1))

def decode_image(filename, img_data, rom_offset):
    img_type, img_frames, img_size1, img_size2, img_size3, img_wh1, img_wh2, img_wh3 = struct.unpack("<BBBBBBBB", img_data[0:8])
    offset = 8
    img_size = img_size1 | (img_size2 << 8) | (img_size3 << 16)
    img_width = img_wh1 | ((img_wh2&0xf) << 8)
    img_height = (img_wh2>>4) | (img_wh3 << 4)
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

    ########for debugging
    debug_str = ""
    if rom_offset >= 0xb0000000:
        for _ in range(len(img_data)):
            debug_str += f"{img_data[_]:02x} "
    print(debug_str)

    if img_type == GDI_IMAGE_TYPE_PNG_SEQUENCE:
        frame_info = []
        frame_data = []
        ext = "png"
        for i in range(img_frames):
            frame_info.append(struct.unpack("<LLL", img_data[offset:offset+12]))
            offset += 12
            print(frame_info[i])
        for i in range(img_frames):
            curr_img_data = img_data[offset:offset+frame_info[i][1]]
            offset += frame_info[i][1]
            frame_data.append(curr_img_data)
            if offset % 4 != 0:
                offset += (4 - (offset % 4))
        
        #########temp create
        temp_png_paths = []
        for i, png_bytes in enumerate(frame_data):
            temp_path = f"{filename}_ext/temp_frame_{i}.{ext}"
            with open(temp_path, "wb") as f:
                f.write(png_bytes)
            temp_png_paths.append(temp_path)

        APNG.from_files(temp_png_paths, delay=frame_info[i][2]).save(f"{filename}_ext/{rom_offset:08x}.png")

        # Clean up temporary files (optional)
        import os
        for p in temp_png_paths:
            os.remove(p)
    elif img_type == GDI_IMAGE_TYPE_BMP_SEQUENCE:
        frame_info = []
        frame_data = []
        ext = "png"
        for i in range(img_frames):
            frame_info.append(struct.unpack("<LLL", img_data[offset:offset+12]))
            offset += 12
            print(frame_info[i])
        for i in range(img_frames):
            curr_img_data = img_data[offset:offset+frame_info[i][1]]
            offset += frame_info[i][1]
            frame_data.append(curr_img_data)
        
        #########temp create
        temp_png_paths = []
        for i, png_bytes in enumerate(frame_data):
            temp_path = f"{filename}_ext/temp_frame_{i}.{ext}"
            with open(temp_path, "wb") as f:
                f.write(png_bytes)
            temp_png_paths.append(temp_path)

        APNG.from_files(temp_png_paths, delay=frame_info[i][2]).save(f"{filename}_ext/{rom_offset:08x}.png")

        # Clean up temporary files (optional)
        import os
        for p in temp_png_paths:
            os.remove(p)
    elif img_type == GDI_IMAGE_TYPE_ABM_SEQUENCE:
        frame_info = []
        frame_data = []
        ext = "png"
        for i in range(img_frames):
            frame_info.append(struct.unpack("<LLL", img_data[offset:offset+12]))
            offset += 12
            print(frame_info[i])
        for i in range(img_frames):
            curr_img_data = img_data[offset:offset+frame_info[i][1]]
            offset += frame_info[i][1]
            frame_data.append(curr_img_data)
            if offset % 4 != 0:
                offset += (4 - (offset % 4))

        #########temp create
        temp_png_paths = []
        for i, png_bytes in enumerate(frame_data):
            temp_path = f"{filename}_ext/temp_frame_{i}.{ext}"
            conv = ab1Decode(png_bytes)
            conv.save(temp_path)
            temp_png_paths.append(temp_path)

        APNG.from_files(temp_png_paths, delay=frame_info[i][2]).save(f"{filename}_ext/{rom_offset:08x}.png")

        # Clean up temporary files (optional)
        import os
        for p in temp_png_paths:
            os.remove(p)
    else:
        img_data = img_data[offset:offset+img_size]
        offset += img_size
        #####debug
        if img_type == GDI_IMAGE_TYPE_ABM:
            conv = ab1Decode(img_data)
            conv.save(f"{filename}_ext/{rom_offset:08x}.png")
        elif img_type == GDI_IMAGE_TYPE_AB2:
            conv = ab2Decode(img_data)
            conv.save(f"{filename}_ext/{rom_offset:08x}.png")
        else:
            open(f"{filename}_ext/{rom_offset:08x}.{ext}", "wb").write(img_data)

if __name__ == "__main__":
    import sys
    fd = open(sys.argv[1], "rb")
    map_offset = int(sys.argv[2], 16)
    groups_offset = int(sys.argv[3], 16)
    reloc_offset = int(sys.argv[4], 16)
    group_count = int(sys.argv[5])
    data = fd.read()
    fd.close()
    os.makedirs(f"{sys.argv[1]}_ext", exist_ok=True)
    group_offsets = []
    group_info = []

    group_count = struct.unpack("<L", data[groups_offset-4:groups_offset])[0]
    map_count = struct.unpack("<L", data[map_offset-4:map_offset])[0]

    data_offsets = []

    for i in range(group_count):
        group_offsets.append(struct.unpack("<L", data[groups_offset+i*4:groups_offset+(i+1)*4])[0]-reloc_offset)
    
    for i in range(group_count):
        hdr = data[group_offsets[i]:group_offsets[i]+4]
        dec_size = ((0xff & hdr[0])<<8) | (0xff & hdr[1])
        lzma_size = ((0xff & hdr[2])<<8) | (0xff & hdr[3])
        dec_data = lzma.decompress(data[group_offsets[i]+4:group_offsets[i]+4+lzma_size])

        offs = 0
        group_entry = []
        while offs < dec_size:
            size = struct.unpack(">L", dec_data[offs:offs+4])[0]
            print(f"group image: size {hex(size)}")
            img_data = dec_data[offs+4:offs+4+size]
            group_entry.append(img_data)
            offs += size+4
        
        group_info.append(group_entry)

    for i in range(map_count):
        idx = struct.unpack("<L", data[map_offset+i*4:map_offset+(i+1)*4])[0]
        print(f"map image: Offset {hex(idx)}")
        if idx < 0xb0000000: #group image
            idx -= reloc_offset
        data_offsets.append(idx)
    
    for i in range(map_count):
        if data_offsets[i] >= 0xb0000000:
            group_idx = ((0x0000FFFF & data_offsets[i]) >> (IMAGE_HANDL_OFFSET_LENGTH + 1))
            img_idx = (((0x0000FFFF & data_offsets[i]) & (~IMAGE_GROUP_MASK)) >> 1)
            print(f"group image: Group {group_idx}, Image {img_idx}")
            img_to_decode = group_info[group_idx][img_idx]
        else:
            print(f"fixed image: Offset {data_offsets[i]}")
            img_to_decode = data[data_offsets[i]:]

        decode_image(sys.argv[1], img_to_decode, data_offsets[i])