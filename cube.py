#!/usr/bin/python3

import ctypes
_LIBMIXUPCUBE_SO = "./libmixupcube.so"

# Maps turn string to turn ID integer
_TURN_IDS = {
    "U": 0,
    "D": 1,
    "F": 2,
    "B": 3,
    "L": 4,
    "R": 5,
    "U'": 6,
    "D'": 7,
    "F'": 8,
    "B'": 9,
    "L'": 10,
    "R'": 11,
    "U2": 12,
    "D2": 13,
    "F2": 14,
    "B2": 15,
    "L2": 16,
    "R2": 17,
}

#
# Helper Functions
#

def _tokenize_turns(turns):
    """
    Turns a string of turns ("UM'L2FB" for example) and returns a list of
    integer turn IDs as defined in _TURN_IDS.

    Max munch parsing: consumes token of length 2 if it can, otherwise it
    consumes a length 1 token.
    """

    ret = []
    i = 0
    while i < len(turns):
        token = _TURN_IDS.get(turns[i:i+2], None)
        if token is None:
            token = _TURN_IDS.get(turns[i:i+1], None)
            i += 1
            if token is None:
                raise ValueError('Unrecognized turn "{}"'.format(turns[i:i+1]))
        else:
            i += 2
        ret.append(token)

    return ret


#
# ctypes Definitions
#

try:
    _libcube = ctypes.cdll.LoadLibrary(_LIBMIXUPCUBE_SO)
except OSError as e:
    if "No such file or directory" in e.message:
        raise OSError('Can\'t find libmixupcube at "{}". Did you forget to '
                      'compile it?'.format(_LIBMIXUPCUBE_SO))
    raise

class _CubieStruct(ctypes.Structure):
    _fields_ = [("id", ctypes.c_byte),
                ("orient", ctypes.c_byte)]

class _CubeStruct(ctypes.Structure):
    _fields_ = [("cubies", _CubieStruct * 26)]
_CubeStruct_p = ctypes.POINTER(_CubeStruct)

# Cube* Cube_new_solved();
_libcube.Cube_new_solved.argtypes = []
_libcube.Cube_new_solved.restype = _CubeStruct_p

# void Cube_turn(Cube* cube, int turn);
_libcube.Cube_turn.argtypes = [_CubeStruct_p, ctypes.c_int]
_libcube.Cube_turn.restype = None

# bool Cube_is_cube_shape(const Cube* cube);
_libcube.Cube_is_cube_shape.argtypes = [_CubeStruct_p]
_libcube.Cube_is_cube_shape.restype = ctypes.c_bool

# bool Cube_is_solved(const Cube* cube);
_libcube.Cube_is_solved.argtypes = [_CubeStruct_p]
_libcube.Cube_is_solved.restype = ctypes.c_bool

# void Cube_free(Cube* cube);
_libcube.Cube_free.argtypes = [_CubeStruct_p]
_libcube.Cube_free.restype = None


class MixupCube():

    def __init__(self):
        #TODO: Support initializing a non-solved cube.
        self._cube = _libcube.Cube_new_solved()

    def __del__(self):
        _libcube.Cube_free(self._cube)

    def __str__(self):
        cubie_list = []
        for cubie in self._cube.contents.cubies:
            cubie_list.append("({}, {})".format(cubie.id, cubie.orient))
        return "[{}]".format(", ".join(cubie_list))

    def is_cube_shape(self):
        return _libcube.Cube_is_cube_shape(self._cube)

    def is_solved(self):
        return _libcube.Cube_is_solved(self._cube)

    def turn(self, turns):
        for t in _tokenize_turns(turns):
            self._turn_once(t)

    def _turn_once(self, turn):
        """Performs a single turn given its turn ID."""
        assert isinstance(turn, int)
        _libcube.Cube_turn(self._cube, turn)

    def draw(self):
        for cubie in self._cube.contents.cubies:
            self._draw_cubie(cubie)

    def _draw_cubie(self, cubie):
        pass  #TODO
