
from math import sqrt
import ctypes

from OpenGL.GL import *
from OpenGL.GLUT import *

_LIBMIXUPCUBE_SO = "./libmixupcube.so"

_TURN_ORDER = [
    "U" , "D" , "F" , "B" , "L" , "R",
    "U2", "D2", "F2", "B2", "L2", "R2",
    "U'", "D'", "F'", "B'", "L'", "R'",
    "M" , "E" , "S",
    "M2", "E2", "S2",
    "M3", "E3", "S3",
    "M4", "E4", "S4",
    "M5", "E5", "S5",
    "M6", "E6", "S6",
    "M'", "E'", "S'",
]
# Maps turn string to turn ID integer
_TURN_IDS = {turn: idx for idx, turn in enumerate(_TURN_ORDER)}

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

_libcube = ctypes.cdll.LoadLibrary(_LIBMIXUPCUBE_SO)

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
        assert turn >= 0 and turn < 39
        _libcube.Cube_turn(self._cube, turn)

    def draw(self):
        """
        Draws cube centered at origin.

        TODO: What are the cube's dimensions and orientation?
        """
        for slot, cubie in enumerate(self._cube.contents.cubies):
            glPushMatrix()
            self._cubie_slot_transform(slot)
            self._draw_cubie(cubie)
            glPopMatrix()

    def _draw_cubie(self, cubie):
        #TODO
        import random
        glColor3f(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
        glutSolidCube(sqrt(2) / 2)

    _CUBIE_COORDINATES = (  # cubie slot index -> (x, y, z)
        # Corners
        (-1, 1, 1), (-1, 1, -1), (1, 1, -1), (1, 1, 1),
        (-1, -1, 1), (-1, -1, -1), (1, -1, -1), (1, -1, 1),
        # Edges
        (0, 1, 1), (-1, 1, 0), (0, 1, -1), (1, 1, 0),
        (-1, 0, 1), (-1, 0, -1), (1, 0, -1), (1, 0, 1),
        (0, -1, 1), (-1, -1, 0), (0, -1, -1), (1, -1, 0),
        # Faces
        (0, 1, 0), (0, 0, 1), (-1, 0, 0),
        (0, 0, -1), (1, 0, 0), (0, -1, 0),
    )
    def _cubie_slot_transform(self, cubie_slot):

        #TODO: Rotation

        # d is the distance in one axis between the center of an edge slot and
        # the center of a corner slot.
        d = sqrt(2) / 2

        x, y, z = MixupCube._CUBIE_COORDINATES[cubie_slot]
        glTranslate(x*d, y*d, z*d)
