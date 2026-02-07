#!/usr/bin/env python

from Modules import ReakoLite_RLSBlock

if __name__ == "__main__":
    import sys
    import os
    rls = ReakoLite_RLSBlock.RLSBlock(sys.argv[1])
    for x, f in enumerate(rls):
        f.save(f"{os.path.splitext(sys.argv[2])[0]}_{x:04d}{os.path.splitext(sys.argv[2])[1]}")
