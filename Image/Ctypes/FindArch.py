# This file is to sum up how to get the hardware architecture (32 or 64 bits)

# solutions are taken from here:
# https://stackoverflow.com/questions/1405913/how-do-i-determine-if-my-python-shell-is-executing-in-32bit-or-64bit-mode-on-os
# https://stackoverflow.com/questions/1842544/how-do-i-detect-if-python-is-running-as-a-64-bit-application

def get_platform():
    """
    Finds if the platform is 32 or 64 bits
    Several different ways are tried in case one fails
    """
    try:
        import platform
        archi_bits = 64 if platform.architecture()[0] == '64bit' else 32
        return archi_bits
    except:
        pass
    try:
        import struct
        archi_bits = struct.calcsize("P") * 8
        return archi_bits
    except:
        pass
    try:
        import ctypes
        archi_bits = ctypes.sizeof(ctypes.c_voidp) * 8
        return archi_bits
    except:
        pass
    try:
        import sys
        archi_bits = 64 if sys.maxsize > 2**32 else 32
        return archi_bits
    except:
        pass
    # default to 32 (is this safe)?
    return 32