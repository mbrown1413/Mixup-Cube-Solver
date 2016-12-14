
import sys
if sys.version_info < (3, 2):
    raise RuntimeError("Python version 3.2 or greater is required")
from math import sqrt
import string
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

# How much to re-orient the cube in x,y,z axes after making a turn. This is
# needed because the C representation always keeps the UFL cubie in the UFL
# slot.
TURN_ORIENT_DELTAS = {
    TURN_IDS["U" ]: ( 0, -1,  0),
    TURN_IDS["U'"]: ( 0,  1,  0),
    TURN_IDS["U2"]: ( 0,  2,  0),
    TURN_IDS["L" ]: ( 1,  0,  0),
    TURN_IDS["L'"]: (-1,  0,  0),
    TURN_IDS["L2"]: ( 2,  0,  0),
    TURN_IDS["F" ]: ( 0,  0, -1),
    TURN_IDS["F'"]: ( 0,  0,  1),
    TURN_IDS["F2"]: ( 0,  0,  2),
}

TURN_AXIS_CORRECTIONS = {
    "U" : "y'",
    "U2": "y2",
    "U'": "y",
    "L" : "x",
    "L2": "x2",
    "L'": "x'",
    "F" : "z'",
    "F2": "z2",
    "F'": "z",
}

class MixupCubeException(Exception):
    pass

class CubieMismatchError(MixupCubeException):
    pass

#
# Helper Functions
#

def _tokenize_turns(turns):
    """
    Takes a string of turns ("UM'L2FB" for example) and returns a list of
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

        turn = None
        for j in (3, 2, 1):
            if turns[i:i+j] in TURN_IDS:
                turn = turns[i:i+j]
                i += j
                break

        if turn is None:
            raise ValueError('Unrecognized turn "{}"'.format(turns[i-1:i]))

        ret.append(turn)

    return ret

def _rotate_turn(axis_turn, turn):
    """
    Takes a turn string and a cube rotation and returns a new turn that is
    equivilent but without the axis rotation.

    Ex: _rotate_turn("y", "R") -> "B"
        The move "y R y'" is equivilent to just "B"
    """
    assert len(axis_turn) <= 2
    axis = axis_turn[0]
    axis_n = 1 if len(axis_turn) == 1 else 3 if axis_turn[1] == "'" else int(axis_turn[1])

    # Assign
    #   t = face or slice being turned
    #   n = number of clockwise turns of `t`
    t = turn[0]
    if len(turn) == 1:
        n = 1
    elif turn[1] == "'" and turn[0] in "MSE":
        n = 7
    elif turn[1] == "'":
        n = 3
    else:
        n = int(turn[1])

    if axis == "x":
        for i in range(axis_n):
            if   t == "U": t,n = "F", n
            elif t == "F": t,n = "D", n
            elif t == "D": t,n = "B", n
            elif t == "B": t,n = "U", n
            elif t == "S": t,n = "E", n
            elif t == "E": t,n = "S", 8 - n
            elif t == "y": t,n = "z", n
            elif t == "z": t,n = "y", 4 - n
            else: break

    elif axis == "y":
        for i in range(axis_n):
            if   t == "F": t,n = "R", n
            elif t == "R": t,n = "B", n
            elif t == "B": t,n = "L", n
            elif t == "L": t,n = "F", n
            elif t == "M": t,n = "S", n
            elif t == "S": t,n = "M", 8 - n
            elif t == "x": t,n = "z", 4 - n
            elif t == "z": t,n = "x", n
            else: break

    elif axis == "z":
        for i in range(axis_n):
            if   t == "U": t,n = "L", n
            elif t == "L": t,n = "D", n
            elif t == "D": t,n = "R", n
            elif t == "R": t,n = "U", n
            elif t == "M": t,n = "E", n
            elif t == "E": t,n = "M", 8 - n
            elif t == "x": t,n = "y", n
            elif t == "y": t,n = "x", 4 - n
            else: break

    else:
        assert False

    # Convert (t, n) to turn string
    assert n != 0
    if n == 1:
        n_str = ""
    elif t in "ESM" and n == 7:
        n_str = "'"
    elif t not in "ESM" and n == 3:
        n_str = "'"
    else:
        n_str = str(n)
    return t + n_str

def _invert_axis_turn(turn):
    if len(turn) == 1:
        return turn + "3"
    assert len(turn) == 2
    if turn[1] == "'":
        return turn[0]
    return turn[0] + str(4-int(turn[1]))

def _eliminate_axis_turns(turns):
    ret = []
    for i in range(len(turns)):
        turn = turns[i]
        if turn[0] in "xyz":
            for j in range(i+1, len(turns)):
                turns[j] = _rotate_turn(turn, turns[j])
        else:
            ret.append(turn)
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


def _parse_c_ints(c_ints):
    raw_turns = []
    i = 0
    while c_ints[i] >= 0:
        raw_turns.append(c_ints[i])
        i += 1
    _libc.free(c_ints)
    return raw_turns

#
# ctypes Definitions
#

_libc = ctypes.cdll.LoadLibrary("libc.so.6")

_libcube = ctypes.cdll.LoadLibrary(_LIBMIXUPCUBE_SO)

class _CubieStruct(ctypes.Structure):
    _fields_ = [("id", ctypes.c_byte),
                ("orient", ctypes.c_byte)]

class _CubeStruct(ctypes.Structure):
    _fields_ = [("cubies", _CubieStruct * 25)]
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

    def __init__(self, cubies=None):
        self._cube = _libcube.Cube_new_solved()

        # A list of axis turns ("x", "y2", "z'", etc.) that put the cube from a
        # normalized orientation (UFL cubie in the UFL slot), which the C
        # representation assumes, to the non-normalized rotation (wherever the
        # UFL cubie logically should be given the sequence of turns applied to
        # this cube).
        self._axis_turns = []

        if cubies:
            assert len(cubies) == 25
            for slot_id, (cubie_id, orient) in enumerate(cubies):
                assert cubie_id < 25
                assert orient < 4
                self._cube.contents.cubies[slot_id].id = cubie_id
                self._cube.contents.cubies[slot_id].orient = orient

    def __str__(self):
        cubie_strs = []
        for cubie in self._cube.contents.cubies:
            cubie_strs.append("{}-{}".format(cubie.id, cubie.orient))
        return '[' + ', '.join(cubie_strs) + ']'

    __repr__ = __str__

    def __eq__(self, other):

        def cubie_equal(cubie_id, cubie1, cubie2):
            if cubie_id <= 18 and cubie1.orient != cubie2.orient:
                return False
            if cubie1.id != cubie2.id:
                return False
            return True

        for i in range(25):
            cubie1 = self._cube.contents.cubies[i]
            cubie2 = other._cube.contents.cubies[i]
            if not cubie_equal(i, cubie1, cubie2):
                return False

        return True

    @classmethod
    def from_str(cls, s):
        """
        Returns a corresponding MixupCube object corresponding to the string.

        You can get valid strings to input here by printing an existing
        MixupCube object. The strings look like this:

            [<id_0>-<orient_0>, <id_1>-<orient_1>, ..., <id_24>-<orient_24>]

        So, for example, a solved cube might look like this:

            [0-0, 1-0, 2-0, 3-0, 4-0, 5-0, 6-0, 7-0, 8-0, 9-0, 10-0, 11-0,
            12-0, 13-0, 14-0, 15-0, 16-0, 17-0, 18-0, 19-0, 20-0, 21-0, 22-0,
            23-0, 24-0]

        The start and end brackets are required, but whitespace is ignored.
        """
        # Remove all whitespace
        whitespace_map = {ord(c):None for c in string.whitespace}
        s = s.translate(whitespace_map)

        assert s.startswith('[')
        assert s.endswith(']')
        s = s[1:-1]

        cubies = []
        for cubie_str in s.split(','):
            assert cubie_str.count('-') == 1
            cubie_id, cubie_orient = cubie_str.split('-')
            cubies.append((int(cubie_id), int(cubie_orient)))
        assert len(cubies) == 25

        return cls(cubies)

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

    def solve(self, _return_turn_list=False):
        """Returns a solution in the form of a string, eg "RU2R'".

        Note an empty string is returned when the cube is already solved.

        """
        return self._solve_abstract(
            _libcube.Cube_solve,
            _return_turn_list
        )

    def solve_to_cube_shape(self, _return_turn_list=False):
        """
        Same as `solve`, but solves to a cube shape instead of the final
        solution.
        """
        return self._solve_abstract(
            _libcube.Cube_solve_to_cube_shape,
            _return_turn_list
        )

    def _solve_abstract(self, solve_func, _return_turn_list=False):
        c_int_list = solve_func(self._cube)
        ints = _parse_c_ints(c_int_list)
        turns = [TURN_STRINGS[t] for t in ints]

        corrected_turns = list(self._axis_turns)
        for turn in turns:
            corrected_turns.append(turn)
            if turn in TURN_AXIS_CORRECTIONS:
                corrected_turns.append(TURN_AXIS_CORRECTIONS[turn])

        return _eliminate_axis_turns(corrected_turns)

    def turn(self, turns):
        """Modifies the cube given a series of turns as a string, eg "RU2R'"."""

        for turn in _tokenize_turns(turns):

            # Orient turns to correct reference frame
            oriented_turn = turn
            for axis_turn in self._axis_turns:
                oriented_turn = _rotate_turn(_invert_axis_turn(axis_turn), oriented_turn)

            turn_id = TURN_IDS[oriented_turn]
            _libcube.Cube_turn(self._cube, turn_id)

            axis_correction = TURN_AXIS_CORRECTIONS.get(oriented_turn, None)
            if axis_correction is not None:
                self._axis_turns.append(axis_correction)

    #
    # Editing
    #

    def rotate_cubie(self, slot_id, amount):
        """Rotates cubie at slot 'slot_id' clockwise `amount` times."""
        assert slot_id >= 0 and slot_id < 25
        self._cube.contents.cubies[slot_id].orient += amount
        if slot_id < 7:
            modulous = 3
        else:
            modulous = 4
        self._cube.contents.cubies[slot_id].orient %= modulous

    def swap_cubies(self, slot_a, slot_b):
        """Swap cubies at slots 'slot_a' and 'slot_b'.

        A corner cannot be swapped with an edge or face. If this happens, a
        CubieMismatchError is raised.

        """
        assert slot_a >= -1 and slot_a < 25
        assert slot_b >= -1 and slot_b < 25
        if slot_a == slot_b: return
        slot_a, slot_b = min(slot_a, slot_b), max(slot_a, slot_b)
        if slot_a < 7 and slot_b >= 7:
            raise CubieMismatchError("Cannot swap a corner with an edge or face.")

        if slot_a == -1:
            raise NotImplementedError("Currently UFL cubie cannot be swapped.")
        else:
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
        The UFL cubie is drawn 25, since it's ID of -1 does not fit in 0-255.

        """
        if selected_slot is not None and slot_id_map:
            raise ValueError("selected_slot and slot_id_map cannot both be specified.")
        if selected_slot is not None:
            assert selected_slot >= -1 and selected_slot < 25

        glPushMatrix()

        # Rotate according to self._axis_turns
        for turn in self._axis_turns:
            axis = turn[0]
            count = 1 if len(turn) == 1 else 3 if turn[1] == "'" else int(turn[1])
            glRotate(90*count, *{
                "x": (1, 0, 0),
                "y": (0, 1, 0),
                "z": (0, 0, 1),
            }[axis])

        ulf_cubie = _CubieStruct(id=-1, orient=0)
        for slot, cubie in enumerate([ulf_cubie] + list(self._cube.contents.cubies), -1):
            glPushMatrix()

            if slot_id_map:
                if slot == -1:
                    glColor3b(25, 25, 25)  # UFL slot fixed in place
                else:
                    glColor3b(slot, slot, slot)

            selected = False
            if selected_slot is not None and selected_slot == slot:
                selected = True

            self._cubie_slot_transform(slot)
            self._draw_cubie(cubie, selected=selected, skip_color=slot_id_map)

            glPopMatrix()

        glPopMatrix()

    def _draw_cubie(self, cubie, selected=False, skip_color=False):
        assert cubie.id >= -1 and cubie.id < 25
        assert cubie.orient >= 0
        if cubie.id < 7:
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

        colors = CUBIE_COLORS[cubie.id+1]  # +1 because ULF has cubie id -1
        if cubie.id < 7:  # Corners
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

        elif cubie.id < 19:  # Edges
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
        assert cubie_slot >= -1 and cubie_slot < 25

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

        x, y, z = SLOT_COORDINATES[cubie_slot+1]  # +1 because the first cubie has id -1
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

        glRotate(SLOT_ROTATIONS[cubie_slot+1][2], 0, 0, 1)
        glRotate(SLOT_ROTATIONS[cubie_slot+1][1], 0, 1, 0)
        glRotate(SLOT_ROTATIONS[cubie_slot+1][0], 1, 0, 0)
