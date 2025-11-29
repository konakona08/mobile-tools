from construct import *
import struct
import csv

StringEntry = Struct(
    "data_ptr" / Int32ub,
    "string_count" / Int32ub,
    "map_ptr" / Int32ub,
    "map_count" / Int32ub,
    "mapsearch_ptr" / Int32ub,
    "mapsearch_count" / Int16ub,
    "is_utf16" / Int16ub
)

def parse_entries(bdata, offset, cnt, reloc_offset):
    entries = []
    for _ in range(cnt):
        print(_)
        entry = StringEntry.parse(bdata[offset:offset+StringEntry.sizeof()])
        ###### some stupidity makes the values be read in big endian
        entry.data_ptr = struct.unpack("<L", entry.data_ptr.to_bytes(4, "big"))[0] - reloc_offset
        entry.string_count = struct.unpack("<L", entry.string_count.to_bytes(4, "big"))[0]
        entry.map_ptr = struct.unpack("<L", entry.map_ptr.to_bytes(4, "big"))[0] - reloc_offset
        entry.map_count = struct.unpack("<L", entry.map_count.to_bytes(4, "big"))[0]
        entry.mapsearch_ptr = struct.unpack("<L", entry.mapsearch_ptr.to_bytes(4, "big"))[0] - reloc_offset
        entry.mapsearch_count = struct.unpack("<H", entry.mapsearch_count.to_bytes(2, "big"))[0]
        entry.is_utf16 = struct.unpack("<H", entry.is_utf16.to_bytes(2, "big"))[0]
        entries.append(entry)
        offset += StringEntry.sizeof()
    return entries

if __name__ == "__main__":
    import sys
    fd = open(sys.argv[1], "rb")
    offset = int(sys.argv[2], 16)
    reloc_offset = int(sys.argv[3], 16)
    count = int(sys.argv[4])
    data = fd.read()
    fd.close()
    entries = parse_entries(data, offset, count, reloc_offset)
    languages = count-2

    # check for dups
    dup_entry = entries[languages]
    dup_data = None
    dup_offset = 0
    if dup_entry.data_ptr:
        dup_data = data[dup_entry.data_ptr:]
        dup_offset = (dup_entry.map_count<<16)|dup_entry.mapsearch_count
        print(dup_offset)
    else:
        dup_offset = 0xffffffff

    # check for fixed
    fixed_entry = entries[count-1]
    print(fixed_entry)
    fixed_data = None
    fixed_map = []
    fixed_isutf16 = 0
    fixed_max_string = 0
    fixed_max_id = 0
    trans_str_cnt = 0
    if fixed_entry.data_ptr:
        fixed_data = data[fixed_entry.data_ptr:]
        fixed_map_data = data[fixed_entry.map_ptr:fixed_entry.map_ptr+(fixed_entry.map_count*4)]
        fixed_str_map_search_data = data[fixed_entry.mapsearch_ptr:fixed_entry.mapsearch_ptr+(fixed_entry.mapsearch_count*6)]
        fixed_max_string = fixed_entry.string_count
        fixed_isutf16 = fixed_entry.is_utf16
        fixed_max_id = fixed_entry.mapsearch_count
        trans_str_cnt = struct.unpack("<H", fixed_str_map_search_data[4:6])[0]
        for a in range(fixed_entry.map_count):
            fixed_map.append(struct.unpack("<H", fixed_map_data[a*2:a*2+2])[0])
        print(fixed_map)

    for i in range(languages):
        entry = entries[i]
        print(f"Processing entry {i}")
        ######Create csv
        f = open(f"{sys.argv[1]}_{i}.csv", "w", newline="")
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["ID", "String"])
        
        string_data = data[entry.data_ptr:]
        string_map_data = data[entry.map_ptr:entry.map_ptr+(entry.map_count*4)]
        string_mapsearch_data = data[entry.mapsearch_ptr:entry.mapsearch_ptr+(entry.mapsearch_count*6)]
        string_map = []
        string_map_search = []

        for a in range(entry.map_count):
            string_map.append(struct.unpack("<L", string_map_data[a*4:a*4+4])[0])
        for a in range(entry.mapsearch_count):
            min_id, max_id, map_offset = struct.unpack("<HHH", string_mapsearch_data[a*6:a*6+6])
            string_map_search.append([min_id, max_id, map_offset])

        for search_curr in string_map_search:
            count = search_curr[1]-search_curr[0]+1
            for a in range(count):
                if search_curr[2]+a >= trans_str_cnt:
                    offset = fixed_map[search_curr[2]+a-trans_str_cnt]<<1
                    str_data = fixed_data[offset:]
                else:
                    offset = string_map[search_curr[2]+a]<<1
                    if offset > dup_offset:
                        offset -= dup_offset
                        str_data = dup_data[offset:]
                    else:
                        str_data = string_data[offset:]
                str_length = 0
                for _ in range(len(str_data)>>1):
                    if str_data[str_length:str_length+2] == b'\0\0':
                        break
                    str_length += 2
                try:
                    writer.writerow([search_curr[0]+a, str_data[:str_length].decode("utf-16-le")])
                except:
                    writer.writerow([search_curr[0]+a, str_data[:str_length]])