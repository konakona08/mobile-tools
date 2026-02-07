from unicorn import *
from unicorn.arm_const import *
from unicorn.arm64_const import *
from unicorn.x86_const import *
from unicorn.mips_const import *

# Page size required by Unicorn
UNICORN_PAGE_SIZE = 0x1000

# Max allowable segment size (1G)
MAX_ALLOWABLE_SEG_SIZE = 1024 * 1024 * 1024

# Alignment functions to align all memory segments to Unicorn page boundaries (4KB pages only)
ALIGN_PAGE_DOWN = lambda x: x & ~(UNICORN_PAGE_SIZE - 1)
ALIGN_PAGE_UP   = lambda x: (x + UNICORN_PAGE_SIZE - 1) & ~(UNICORN_PAGE_SIZE-1)

class UnicornSimpleHeap(object):
    """ Use this class to provide a simple heap implementation. This should
        be used if malloc/free calls break things during emulation. This heap also
        implements basic guard-page capabilities which enable immediate notice of
        heap overflow and underflows.
    """

    # Helper data-container used to track chunks
    class HeapChunk(object):
        def __init__(self, actual_addr, total_size, data_size):
            self.total_size = total_size                        # Total size of the chunk (including padding and guard page)
            self.actual_addr = actual_addr                      # Actual start address of the chunk
            self.data_size = data_size                          # Size requested by the caller of actual malloc call
            self.data_addr = actual_addr + UNICORN_PAGE_SIZE    # Address where data actually starts

        # Returns true if the specified buffer is completely within the chunk, else false
        def is_buffer_in_chunk(self, addr, size):
            if addr >= self.data_addr and ((addr + size) <= (self.data_addr + self.data_size)):
                return True
            else:
                return False

    # Skip the zero-page to avoid weird potential issues with segment registers
    HEAP_MIN_ADDR = 0x08000000
    HEAP_MAX_ADDR = 0x0fffffff

    _uc = None              # Unicorn engine instance to interact with
    _chunks = []            # List of all known chunks
    _debug_print = False    # True to print debug information

    def __init__(self, uc, debug_print=False):
        self._uc = uc
        self._debug_print = debug_print

        # Add the watchpoint hook that will be used to implement psuedo-guard page support
        self._uc.hook_add(UC_HOOK_MEM_WRITE | UC_HOOK_MEM_READ, self.__check_mem_access)

    def malloc(self, size):
        # Figure out the overall size to be allocated/mapped
        #    - Allocate at least 1 4k page of memory to make Unicorn happy
        #    - Add guard pages at the start and end of the region
        total_chunk_size = UNICORN_PAGE_SIZE + ALIGN_PAGE_UP(size) + UNICORN_PAGE_SIZE
        # Gross but efficient way to find space for the chunk:
        chunk = None
        for addr in range(self.HEAP_MIN_ADDR, self.HEAP_MAX_ADDR, UNICORN_PAGE_SIZE):
            try:
                self._uc.mem_map(addr, total_chunk_size, UC_PROT_READ | UC_PROT_WRITE)
                chunk = self.HeapChunk(addr, total_chunk_size, size)
                if self._debug_print:
                    print("Allocating 0x{0:x}-byte chunk @ 0x{1:016x}".format(chunk.data_size, chunk.data_addr))
                break
            except UcError as e:
                continue
        # Something went very wrong
        if chunk == None:
            return 0
        self._chunks.append(chunk)
        return chunk.data_addr

    def calloc(self, size, count):
        # Simple wrapper around malloc with calloc() args
        return self.malloc(size*count)

    def realloc(self, ptr, new_size):
        # Wrapper around malloc(new_size) / memcpy(new, old, old_size) / free(old)
        if self._debug_print:
            print("Reallocating chunk @ 0x{0:016x} to be 0x{1:x} bytes".format(ptr, new_size))
        old_chunk = None
        for chunk in self._chunks:
            if chunk.data_addr == ptr:
                old_chunk = chunk
        new_chunk_addr = self.malloc(new_size)
        if old_chunk != None:
            self._uc.mem_write(new_chunk_addr, str(self._uc.mem_read(old_chunk.data_addr, old_chunk.data_size)))
            self.free(old_chunk.data_addr)
        return new_chunk_addr

    def free(self, addr):
        for chunk in self._chunks:
            if chunk.is_buffer_in_chunk(addr, 1):
                if self._debug_print:
                    print("Freeing 0x{0:x}-byte chunk @ 0x{0:016x}".format(chunk.req_size, chunk.data_addr))
                self._uc.mem_unmap(chunk.actual_addr, chunk.total_size)
                self._chunks.remove(chunk)
                return True
        return False

    # Implements basic guard-page functionality
    def __check_mem_access(self, uc, access, address, size, value, user_data):
        for chunk in self._chunks:
            if address >= chunk.actual_addr and ((address + size) <= (chunk.actual_addr + chunk.total_size)):
                if chunk.is_buffer_in_chunk(address, size) == False:
                    if self._debug_print:
                        print("Heap over/underflow attempting to {0} 0x{1:x} bytes @ {2:016x}".format( \
                            "write" if access == UC_MEM_WRITE else "read", size, address))
                    # Force a memory-based crash
                    uc.force_crash(UcError(UC_ERR_READ_PROT))