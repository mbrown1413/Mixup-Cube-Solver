
import os
import sys
if sys.version_info < (3, 2):
    raise RuntimeError("Python version 3.2 or greater is required")
import ctypes

_LIBMIXUPCUBE_SO = "./libmixupcube.so"

_libcube = ctypes.cdll.LoadLibrary(_LIBMIXUPCUBE_SO)

# bool Heuristic_generate(const char* name);
_libcube.Heuristic_generate.argtypes = [ctypes.POINTER(ctypes.c_char)]
_libcube.Heuristic_generate.restype = ctypes.c_bool

HEURISTICS_DIR = "heuristics/"

def main():

    if len(sys.argv) < 2:
        print("Usage: {} <heuristic_name> [<heuristic_name [...]]".format(sys.argv[0]))
        return -1
    names = sys.argv[1:]

    # This makes sure the C code saves heuristics in the correct directory.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Make sure heuristics directory exists.
    if not os.path.isdir(HEURISTICS_DIR):
        if os.path.exists(HEURISTICS_DIR):
            print("Heuristics directory {} is a file, but it should be a directory! Please delete it and try again.".format(HEURISTICS_DIR))
            return -1
        os.mkdir(HEURISTICS_DIR)

    for name in names:
        _libcube.Heuristic_generate(bytes(name, "utf-8"))

    return 0

if __name__ == "__main__":
    sys.exit(main())
