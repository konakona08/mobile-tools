#!/usr/bin/env python

from Modules import ReakoLite_R20

if __name__ == "__main__":
    import sys
    import os
    r20 = ReakoLite_R20.ReakoR20(sys.argv[1])
    for x, f in enumerate(r20):
        f.save(f"{os.path.splitext(sys.argv[2])[0]}_{x:04d}{os.path.splitext(sys.argv[2])[1]}")
