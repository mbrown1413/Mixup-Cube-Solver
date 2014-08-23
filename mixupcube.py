
import sys
if sys.version_info < (3, 2):
    raise RuntimeError("Python version 3.2 or greater is required")
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
TURN_IDS = {turn: idx for idx, turn in enumerate(_TURN_ORDER)}

# Maps turn ID integer to turn string
TURN_STRINGS = {idx: turn for idx, turn in enumerate(_TURN_ORDER)}

class MixupCubeException(Exception):
    pass

class CubieMismatchError(MixupCubeException):
    pass

#
# Helper Functions
#

def _tokenize_turns(turns):
    """
    Turns a string of turns ("UM'L2FB" for example) and returns a list of
    integer turn IDs as defined in TURN_IDS. Ignores spaces.

    Max munch parsing: consumes token of length 2 if it can, otherwise it
    consumes a length 1 token.
    """

    ret = []
    i = 0
    while i < len(turns):
        if turns[i].isspace():
            i += 1
            continue
        token = TURN_IDS.get(turns[i:i+2], None)
        if token is None:
            token = TURN_IDS.get(turns[i:i+1], None)
            i += 1
            if token is None:
                raise ValueError('Unrecognized turn "{}"'.format(turns[i-1:i]))
        else:
            i += 2
        ret.append(token)

    return ret

def _draw_inset_rect(p0, p1, p2, p3, void_color):
    INSET_AMOUNT = 0.025
    p0 = numpy.array(p0)
    p1 = numpy.array(p1)
    p2 = numpy.array(p2)
    p3 = numpy.array(p3)

    def move_towards(a, b, amount):
        """Move `a` towards `b` by `amount`"""
        vec = b - a
        vec = vec / numpy.linalg.norm(vec)
        return a + vec*amount

    # Create 4 inset points, closer to the center by INSET_AMOUNT
    center = (p0 + p1 + p2 + p3) / 4
    i0 = move_towards(p0, center, INSET_AMOUNT)
    i1 = move_towards(p1, center, INSET_AMOUNT)
    i2 = move_towards(p2, center, INSET_AMOUNT)
    i3 = move_towards(p3, center, INSET_AMOUNT)

    # Draw shrunk rectangle
    glVertex(*i0)
    glVertex(*i1)
    glVertex(*i2)
    glVertex(*i3)

    # Draw 4 trapezoids bordering the rectangle
    to_draw = (
        p0, p1, i1, i0,
        p1, p2, i2, i1,
        p2, p3, i3, i2,
        p3, p0, i0, i3,
    )
    if void_color is not None:
        glColor(void_color)
    for p in to_draw:
        glVertex(*p)


def _parse_raw_solution(raw_ints):
    raw_turns = []
    i = 0
    while raw_ints[i] >= 0:
        raw_turns.append(raw_ints[i])
        i += 1
    _libc.free(raw_ints)

    turns = [TURN_STRINGS[t] for t in raw_turns]
    return ''.join(turns)

#
# ctypes Definitions
#

_libc = ctypes.cdll.LoadLibrary("libc.so.6")

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

# int* Cube_solve(const Cube* cube);
_libcube.Cube_solve.argtypes = [_CubeStruct_p]
_libcube.Cube_solve.restype = ctypes.POINTER(ctypes.c_int)

# int* Cube_solve_to_cube_shape(const Cube* cube);
_libcube.Cube_solve_to_cube_shape.argtypes = [_CubeStruct_p]
_libcube.Cube_solve_to_cube_shape.restype = ctypes.POINTER(ctypes.c_int)


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
    # ctypes wrappers
    #

    def __del__(self):
        _libcube.Cube_free(self._cube)

    def is_cube_shape(self):
        """Is this puzzle in a cube shape? Returns True or False accordingly."""
        return _libcube.Cube_is_cube_shape(self._cube)

    def is_solved(self):
        """Is this cube solved? Returns True or False accordingly."""
        return _libcube.Cube_is_solved(self._cube)

    def solve(self):
        """Returns a solution in the form of a string, eg "RU2R'".

        Note an empty string is returned when the cube is already solved.

        """
        raw_ints = _libcube.Cube_solve(self._cube)
        return _parse_raw_solution(raw_ints)

    def solve_to_cube_shape(self):
        """
        Same as `solve`, but solves to a cube shape instead of the final
        solution.
        """
        raw_ints = _libcube.Cube_solve_to_cube_shape(self._cube)
        return _parse_raw_solution(raw_ints)

    def turn(self, turns):
        """Modifies the cube given a series of turns as a string, eg "RU2R'"."""
        for t in _tokenize_turns(turns):
            self._turn_once(t)

    def _turn_once(self, turn):
        """Performs a single turn given its turn ID."""
        assert isinstance(turn, int)
        assert turn >= 0 and turn < 39
        _libcube.Cube_turn(self._cube, turn)

    #
    # Editing
    #

    def rotate_cubie(self, slot_id, amount):
        """Rotates cubie at slot 'slot_id' clockwise `amount` times."""
        assert slot_id >= 0 and slot_id < 26
        self._cube.contents.cubies[slot_id].orient += amount
        if slot_id < 8:
            modulous = 3
        else:
            modulous = 4
        self._cube.contents.cubies[slot_id].orient %= modulous

    def swap_cubies(self, slot_a, slot_b):
        """Swap cubies at slots 'slot_a' and 'slot_b'.

        A corner cannot be swapped with an edge or face. If this happens, a
        CubieMismatchError is raised.

        """
        assert slot_a >= 0 and slot_a < 26
        assert slot_b >= 0 and slot_b < 26
        slot_a, slot_b = min(slot_a, slot_b), max(slot_a, slot_b)
        if slot_a < 8 and slot_b >= 8:
            raise CubieMismatchError("Cannot swap a corner with an edge or face.")
        a = self._cube.contents.cubies[slot_a].id
        b = self._cube.contents.cubies[slot_b].id
        self._cube.contents.cubies[slot_a].id = b
        self._cube.contents.cubies[slot_b].id = a

    #
    # Drawing
    #

    def draw(self, selected_slot=None, slot_id_map=False):
        """
        Draws cube centered at origin.

        When the puzzle is a cube shape, it will be 1x1x1 units long. Note that
        when it's not in cube form, it will be a bit larger than 1x1x1; an edge
        cubie in a face slot will stick out by (sqrt(2)-1)/2. The R, U, and F
        faces point to the x, y and z axes respectively.

        If selected_slot is given, it must be the id of a slot to highlight.

        If slot_id_map is True, instead of drawing colors, the red, green and
        blue channels are set to the cubie slot drawn at that position. Use
        this option to map a pixel position back to a slot id. Note that you'll
        have to clear the depth buffer and clear the color buffer to 255 first.

        """
        if selected_slot is not None and slot_id_map:
            raise ValueError("selected_slot and slot_id_map cannot both be specified.")
        if selected_slot:
            assert selected_slot >= 0 and selected_slot < 26

        for slot, cubie in enumerate(self._cube.contents.cubies):
            glPushMatrix()

            if slot_id_map:
                glColor3b(slot, slot, slot)

            selected = False
            if selected_slot is not None and selected_slot == slot:
                selected = True

            self._cubie_slot_transform(slot)
            self._draw_cubie(cubie, selected=selected, skip_color=slot_id_map)

            glPopMatrix()

    def _draw_cubie(self, cubie, selected=False, skip_color=False):
        assert cubie.id >= 0 and cubie.id < 26
        assert cubie.orient >= 0
        if cubie.id < 8:
            assert cubie.orient < 3
        else:
            assert cubie.orient < 4

        if skip_color:
            void_color = None
        elif selected:
            void_color = (0, 1, 1)
        else:
            void_color = COLOR_VOID

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
            if not skip_color:
                glColor3fv(colors[0])
            _draw_inset_rect((-s2, s2,  s2),
                             (-s2, s2, -s2),
                             ( s2, s2, -s2),
                             ( s2, s2,  s2), void_color)
            # Left
            if not skip_color:
                glColor3fv(colors[1])
            _draw_inset_rect((-s2,  s2,  s2),
                             (-s2, -s2,  s2),
                             (-s2, -s2, -s2),
                             (-s2,  s2, -s2), void_color)
            # Front
            if not skip_color:
                glColor3fv(colors[2])
            _draw_inset_rect((-s2,  s2, s2),
                             ( s2,  s2, s2),
                             ( s2, -s2, s2),
                             (-s2, -s2, s2), void_color)
            # Opposite hidden sides
            # These could be shown if an edge is in a face slot
            if not skip_color:
                glColor3fv(void_color)
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
            if not skip_color:
                glColor3fv(colors[0])
            _draw_inset_rect((-l2, 0,  l2),
                             (-l2, l2,  0),
                             ( l2, l2,  0),
                             ( l2, 0,  l2), void_color)
            # Top
            if not skip_color:
                glColor3fv(colors[1])
            _draw_inset_rect((-l2, l2,  0),
                             (-l2, 0, -l2),
                             ( l2, 0, -l2),
                             ( l2, l2,  0), void_color)
            glEnd()
            # Side triangles
            if not skip_color:
                glColor3fv(void_color)
            glBegin(GL_TRIANGLES)
            glVertex(-l2, 0,  l2)  # Left
            glVertex(-l2, 0, -l2)
            glVertex(-l2, l2,  0)
            glVertex( l2, 0,  l2)  # Right
            glVertex( l2, l2,  0)
            glVertex( l2, 0, -l2)
            glEnd()

        else:  # Faces
            if not skip_color:
                glColor3fv(colors[0])
            glBegin(GL_QUADS)
            _draw_inset_rect(( l2, 0,  l2),
                             (-l2, 0,  l2),
                             (-l2, 0, -l2),
                             ( l2, 0, -l2), void_color)
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
