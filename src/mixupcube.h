#ifndef CUBE_H
#define CUBE_H

#include <stdio.h>
#include <stdbool.h>

/**
 * The 3x3x3 Mixup Rubik's Cube type.
 *
 * The puzzle is represented by a list of 26 cubies. A cubie is a physical
 * corner (3 sides), edge (2 sides), or face (1 side) piece. There are 8
 * corners, 12 edges, and 6 faces, stored in that order. The Mixup Cube isn't
 * like a normal Rubik's cube: center faces can occupy edge piece slots and
 * vice versa. The moves allow turning any center slice by 45 degrees.
 *
 * For each cubie we store an orientation and an ID.
 *
 * Cubie ID
 * ========
 *
 * The ID is based on the cubie's position at the solved state. Well, there are
 * actually 6 solved states (rotating the whole cube each of 6 ways), but we'll
 * choose one for now and let the solve function worry about that. Here is the
 * solved cube we're interested in:
 *
 * 01 10 02
 *         \
 * 13 23 14 \
 *           \
 * 05 18 06   \
 *  \          \
 *   \          \
 *    \   09 20 11
 *     \          \
 *      \ 22    24 \
 *       \          \
 *        17 25 19   \
 *         \          \
 *          \          \
 *           \   00 08 03
 *            \
 *             \ 12 21 15
 *              \
 *               04 16 07
 *
 * For each piece type, the IDs are ordered from top to bottom, front to back,
 * and clockwise. The IDs are unique between cubie types to make it easy to
 * tell when an edge is in a face slot, the ID values stored for each type are:
 *
 *  0 -  7  Corners
 *  8 - 19  Edges
 * 20 - 25  Faces
 *
 * Although we don't store the colors themselves in this internal
 * representation, here are the face colors:
 *
 *  ID  Cubie  Dir   Color
 *  --  ----- -----  -----
 *  20   F0    Top    White
 *  21   F1    Front  Red
 *  22   F2    Left   Green
 *  23   F3    Back   Orange
 *  24   F4    Right  Blue
 *  25   F5    Down   Yellow
 *
 * Cubie Orientation
 * =================
 *
 * Every cubie has orientation 0 at its solved slot in the solved state
 * described above. Adding one rotates it clockwise, and subtracting one
 * rotates counter-clockwise. Corners have rotation between 0-2 inclusive and
 * edges are 0-3. For faces, the orientation is treated just like edges, except
 * we don't actually care what the value is. We mask out the face orientation
 * before checking if the cube is solved.
 *
 * What if the cubie isn't in its solved slot? For each cubie type, we'll
 * define a unique way to get every cubie back into its solved slot. Or at
 * least unique enough to prevent the orientation from being affected. To find
 * out a cubie's rotation, just move it to its solved slot in this unique way,
 * then count the number of times the cubie has been rotated clockwise from its
 * solved orientation.
 *
 * For corners, the moves allowed are U, D, F2, B2, L2 and R2. So F, B, L and R
 * must be turned 180 degrees, while U and D can be turned by any increment of
 * 90 degrees. Although this doesn't define a completely unique way to move the
 * cubie to its solved slot, the orientation will always be the same. You can
 * think of this as keeping the cube within a group (where each group member is
 * a cube state). One interesting thing to note is that a corner has
 * orientation 0 if and only if its white (Up) or yellow (Down) face is on
 * either the U or D face.
 *
 * Edges are a bit trickier. For now, assume the edge is in an edge slot, not a
 * face slot. The moves allowed are U, D, F, B, L2 and R2. Allowing F and B to
 * turn by 90 degrees allows the cubies in the E slice (FL, FR, etc.) to move
 * freely. If the edge is in a face slot, we'll define a unique way to get it
 * back into an edge slot, then you can apply the previous rule like normal. If
 * the cubie is in the U, D, F or B face slot, make the move M. If the cubie is
 * in the L or R face slot, make the move E.
 *
 */
typedef struct {
    unsigned char id;
    unsigned char orient;
} Cubie;

typedef struct {
    Cubie cubies[26];
} Cube;

static const int N_TURN_TYPES = 39;

/**
 * This enum can be used to identify either cubie slots in the cube, or for a
 * cubie ID (since the cubie ID is the cubie's placement at the solved state).
 * The letters indicating the faces (Up, Down, Front, Back, Left and Right) are
 * always in the order UDFBLR. For example, the corner cubie at the
 * intersection of the upper, front and left faces is identified as CUBIE_UFL.
 * The edge cubie at the intersection of the front and left faces is identified
 * as CUBIE_FL.
 */
enum CubieId {
    CUBIE_UFL, CUBIE_UBL, CUBIE_UBR, CUBIE_UFR,
    CUBIE_DFL, CUBIE_DBL, CUBIE_DBR, CUBIE_DFR,
    CUBIE_UF, CUBIE_UL, CUBIE_UB, CUBIE_UR,
    CUBIE_FL, CUBIE_BL, CUBIE_BR, CUBIE_FR,
    CUBIE_DF, CUBIE_DL, CUBIE_DB, CUBIE_DR,
    CUBIE_U, CUBIE_F, CUBIE_L, CUBIE_B, CUBIE_R, CUBIE_D,
};

/**
 * Allocates a new cube in the solved state.
 */
Cube* Cube_new_solved();

/**
 * Copies the cube from src to dst.
 */
void Cube_copy(Cube* dst, const Cube* src);

/**
 * Turn either a face or a slice.
 *
 * There are 39 possible turns, the turn argument must be from 0-38 inclusive.
 * All possible turns are:
 *   *  0 to  5 - U,  D,  F,  B,  L  and R.  90 degree clockwise face turns.
 *   *  6 to 11 - U2, D2, F2, B2, L2 and R2. Same as 0-5 repeated twice.
 *   * 12 to 17 - U', D', F', B', L' and R'. Same as 0-5 repeated thrice.
 *   * 18 to 20 - M, E and S. Slice turns.
 *   * 21 to 38 - Same as 18 to 20, repeated 2 to 7 times.
 */
void Cube_turn(Cube* cube, int turn);

/**
 * Returns true if the puzzle is in a cube shape. For this to happen, all of
 * the edge slots must have edges in them, and the edges must have either 0 or
 * 2 rotation.
 */
bool Cube_is_cube_shape(const Cube* cube);

/**
 * Is this cube solved? Returns true or false.
 */
bool Cube_is_solved(const Cube* cube);

/**
 * Return a list of turns to solve the given cube.
 *
 * The integer list returned is a list of turns, as described in the
 * documentation for Cube_turn, terminated with a -1 at the end. If
 * solution_length_out is not NULL, it is set to the length of the solution.
 *
 * Don't forget to free the return value!
 */
int* Cube_solve(const Cube* cube, int* solution_length_out);

/**
 * Print the cube as a list of (id, orientation).
 */
void Cube_print(FILE* out, const Cube* cube);

/**
 * Free a cube previously allocated with a Cube_new_* function.
 */
void Cube_free(Cube* cube);

#endif
