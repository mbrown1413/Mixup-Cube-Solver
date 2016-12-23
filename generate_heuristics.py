
import os
import sys
import ctypes

_LIBMIXUPCUBE_SO = "./libmixupcube.so"

_libcube = ctypes.cdll.LoadLibrary(_LIBMIXUPCUBE_SO)

# bool Heuristics_generate();
_libcube.Heuristics_generate.argtypes = []
_libcube.Heuristics_generate.restype = ctypes.c_bool

HEURISTICS_DIR = "heuristics/"

def main():

    # This makes sure the C code saves heuristics in the correct directory.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Make sure heuristics directory exists.
    if not os.path.isdir(HEURISTICS_DIR):
        if os.path.exists(HEURISTICS_DIR):
            print("Heuristics directory {} is a file, but it should be a directory! Please delete it and try again.".format(HEURISTICS_DIR))
            return -1
        os.mkdir(HEURISTICS_DIR)

    ret = _libcube.Heuristics_generate()
    if not ret:
        return -1

    return 0

if __name__ == "__main__":
    sys.exit(main())
