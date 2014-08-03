
from math import sqrt
import ctypes

import numpy

from OpenGL.GL import *
from OpenGL.GLUT import *

COLOR_U = (1, 1, 1)
COLOR_D = (1, 1, 0)
COLOR_F = (1, 0, 0)
COLOR_B = (1, 0.5, 0)
COLOR_L = (0, 1, 0)
COLOR_R = (0, 0, 1)
COLOR_VOID = (0.1, 0.1, 0.1)

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

def _draw_inset_rect(p0, p1, p2, p3):
    INSET_AMOUNT = 0.02
    p0 = numpy.array(p0)
    p1 = numpy.array(p1)
    p2 = numpy.array(p2)
    p3 = numpy.array(p3)

    def move_towards(a, b, amount):
        """Move `a` towards `b` by `amount`"""
        vec = b - a
        vec = vec / numpy.linalg.norm(vec)
        return a + vec*amount

    center = (p0 + p1 + p2 + p3) / 4
    p4 = move_towards(p0, center, INSET_AMOUNT)
    p5 = move_towards(p1, center, INSET_AMOUNT)
    p6 = move_towards(p2, center, INSET_AMOUNT)
    p7 = move_towards(p3, center, INSET_AMOUNT)

    glVertex(*p4)
    glVertex(*p5)
    glVertex(*p6)
    glVertex(*p7)

    glColor(COLOR_VOID)

    glVertex(*p0)
    glVertex(*p1)
    glVertex(*p5)
    glVertex(*p4)

    glVertex(*p1)
    glVertex(*p2)
    glVertex(*p6)
    glVertex(*p5)

    glVertex(*p2)
    glVertex(*p3)
    glVertex(*p7)
    glVertex(*p6)

    glVertex(*p3)
    glVertex(*p0)
    glVertex(*p4)
    glVertex(*p7)

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

    def __str__(self):
        cubie_list = []
        for cubie in self._cube.contents.cubies:
            cubie_list.append("({}, {})".format(cubie.id, cubie.orient))
        return "[{}]".format(", ".join(cubie_list))

    #
    # Ctypes wrappers
    #

    def __del__(self):
        _libcube.Cube_free(self._cube)

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

    #
    # Drawing
    #

    def draw(self):
        """
        Draws cube centered at origin.

        When the puzzle is a cube shape, its 3 sides will be length 1. Note
        that when it's not in cube form, it will be a bit larger than 1x1x1 (an
        edge cubie in a face slot will stick out by (sqrt(2)-1)/2 ). The x, y,
        and z axes point to the R, U and F faces respectively.

        """
        for slot, cubie in enumerate(self._cube.contents.cubies):
            glPushMatrix()
            try:
                self._cubie_slot_transform(slot)
                self._draw_cubie(cubie)
            finally:
                glPopMatrix()

    def _draw_cubie(self, cubie):
        assert cubie.id >= 0 and cubie.id < 26
        assert cubie.orient >= 0
        if cubie.id < 8:
            assert cubie.orient < 3
        else:
            assert cubie.orient < 4

        # s - Short, l - Long
        # These distances are the key dimensions of each of the 3 cubie types.
        # s is the length of a corner cubie and also the short side of an edge
        # cubie. l is the length of a face cubie and also the long side of an
        # edge cubie. These values are chosen so the length of the whole cubie
        # is 1x1x1 units.
        s = 1 - sqrt(2)/2
        l = sqrt(2) - 1
        s2 = s / 2
        l2 = l / 2

        CUBIE_COLORS = (
            # Corners
            (COLOR_U, COLOR_L, COLOR_F), (COLOR_U, COLOR_B, COLOR_L),
            (COLOR_U, COLOR_R, COLOR_B), (COLOR_U, COLOR_F, COLOR_R),
            (COLOR_D, COLOR_F, COLOR_L), (COLOR_D, COLOR_L, COLOR_B),
            (COLOR_D, COLOR_B, COLOR_R), (COLOR_D, COLOR_R, COLOR_F),
            # Edges
            (COLOR_F, COLOR_U), (COLOR_L, COLOR_U),
            (COLOR_B, COLOR_U), (COLOR_R, COLOR_U),
            (COLOR_F, COLOR_L), (COLOR_B, COLOR_L),
            (COLOR_B, COLOR_R), (COLOR_F, COLOR_R),
            (COLOR_F, COLOR_D), (COLOR_L, COLOR_D),
            (COLOR_B, COLOR_D), (COLOR_R, COLOR_D),
            # Faces
            (COLOR_U,), (COLOR_F,), (COLOR_L,),
            (COLOR_B,), (COLOR_R,), (COLOR_D,),
        )

        colors = CUBIE_COLORS[cubie.id]
        if cubie.id < 8:  # Corners
            glRotate(120*cubie.orient, 1, -1, -1)
            glBegin(GL_QUADS)
            # Top
            glColor3fv(colors[0])
            _draw_inset_rect((-s2, s2,  s2),
                             (-s2, s2, -s2),
                             ( s2, s2, -s2),
                             ( s2, s2,  s2))
            # Left
            glColor3fv(colors[1])
            _draw_inset_rect((-s2,  s2,  s2),
                             (-s2, -s2,  s2),
                             (-s2, -s2, -s2),
                             (-s2,  s2, -s2))
            # Front
            glColor3fv(colors[2])
            _draw_inset_rect((-s2,  s2, s2),
                             ( s2,  s2, s2),
                             ( s2, -s2, s2),
                             (-s2, -s2, s2))
            # Opposite hidden sides
            # These could be shown if an edge is in a face slot
            glColor3fv(COLOR_VOID)
            glVertex(-s2, -s2,  s2)
            glVertex(-s2, -s2, -s2)
            glVertex( s2, -s2, -s2)
            glVertex( s2, -s2,  s2)
            glVertex(s2,  s2,  s2)
            glVertex(s2, -s2,  s2)
            glVertex(s2, -s2, -s2)
            glVertex(s2,  s2, -s2)
            glVertex(-s2,  s2, -s2)
            glVertex( s2,  s2, -s2)
            glVertex( s2, -s2, -s2)
            glVertex(-s2, -s2, -s2)
            glEnd()

        elif cubie.id < 20:  # Edges
            glRotate(90*cubie.orient, 0, -1, 0)
            glBegin(GL_QUADS)
            # Front
            glColor3fv(colors[0])
            _draw_inset_rect((-l2, 0,  l2),
                             (-l2, l2,  0),
                             ( l2, l2,  0),
                             ( l2, 0,  l2))
            # Top
            glColor3fv(colors[1])
            _draw_inset_rect((-l2, l2,  0),
                             (-l2, 0, -l2),
                             ( l2, 0, -l2),
                             ( l2, l2,  0))
            glEnd()
            # Side triangles
            glColor3fv(COLOR_VOID)
            glBegin(GL_TRIANGLES)
            glVertex(-l2, 0,  l2)  # Left
            glVertex(-l2, 0, -l2)
            glVertex(-l2, l2,  0)
            glVertex( l2, 0,  l2)  # Right
            glVertex( l2, l2,  0)
            glVertex( l2, 0, -l2)
            glEnd()

        else:  # Faces
            glColor3fv(colors[0])
            glBegin(GL_QUADS)
            _draw_inset_rect(( l2, 0,  l2),
                             (-l2, 0,  l2),
                             (-l2, 0, -l2),
                             ( l2, 0, -l2))
            glEnd()

    def _cubie_slot_transform(self, cubie_slot):
        assert cubie_slot >= 0 and cubie_slot < 26

        # d is the distance in one axis between the center of an edge slot and
        # the center of a corner slot.
        d = sqrt(2) / 4

        SLOT_COORDINATES = (  # cubie slot index -> (x, y, z)
            # Corners
            (-d,  d, d), (-d,  d, -d), (d,  d, -d), (d,  d, d),
            (-d, -d, d), (-d, -d, -d), (d, -d, -d), (d, -d, d),
            # Edges
            ( 0,  d, d), (-d,  d,  0), (0,  d, -d), (d,  d, 0),
            (-d,  0, d), (-d,  0, -d), (d,  0, -d), (d,  0, d),
            ( 0, -d, d), (-d, -d,  0), (0, -d, -d), (d, -d, 0),
            # Faces
            (0, 0.5,  0), (0, 0, 0.5), (-0.5,  0, 0),
            (0, 0, -0.5), (0.5, 0, 0), ( 0, -0.5, 0),
        )

        x, y, z = SLOT_COORDINATES[cubie_slot]
        glTranslate(x, y, z)

        # How much (in degrees) to rotate for each cubie slot about the x, y,
        # and z axes. Before rotation each corner is drawn as if it were in the
        # UFL slot, and edges/faces are drawn as if they were in the U slot.
        SLOT_ROTATIONS = (
            # Corners
            (0, 0, 0), (0, -90, 0), (0, 180, 0), (0, 90, 0),
            (180, 90, 0), (180, 0, 0), (180, -90, 0), (180, 180, 0),
            # Edges
            (45, 0, 0), (45, -90, 0), (45, 180, 0), (45, 90, 0),
            (45, 0, 90), (45, 180, 90), (45, 180, -90), (45, 0, -90),
            (45, 0, 180), (45, 90, 180), (45, 180, 180), (45, -90, 180),
            # Faces
            (0, 0, 0), (90, 0, 180), (0, 0, 90),
            (-90, 0, 180), (0, 180, -90), (180, 0, 0),
        )

        glRotate(SLOT_ROTATIONS[cubie_slot][2], 0, 0, 1)
        glRotate(SLOT_ROTATIONS[cubie_slot][1], 0, 1, 0)
        glRotate(SLOT_ROTATIONS[cubie_slot][0], 1, 0, 0)
