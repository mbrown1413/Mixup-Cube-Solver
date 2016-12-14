#ifndef CUBE_H
#define CUBE_H

#include <stdio.h>
#include <stdbool.h>

/**
 * The 3x3x3 Mixup Rubik's Cube type.
 *
 * The puzzle is represented by a list of 25 cubies. A cubie is a physical
 * corner (3 sides), edge (2 sides), or face (1 side) piece. There are 8
 * corners (one is fixed in place and not stored), 12 edges, and 6 faces,
 * stored in that order. The Mixup Cube isn't like a normal Rubik's cube:
 * center faces can occupy edge piece slots and vice versa. The moves allow
 * turning any center slice by 45 degrees.
 *
 * For each cubie we store an orientation and an ID.
 *
 * Cubie ID
 * ========
 *
 * Each place a cubie can be is called a slot. Each slot has an ID from 0 to
 * 24. A cubie's ID is based on the cubie's position at the solved state. Here
 * are the IDs for each slot:
 *
 * 00 09 01
 *         \
 * 12 22 13 \
 *           \
 * 04 17 05   \
 *  \          \
 *   \          \
 *    \   08 19 10
 *     \          \
 *      \ 21    23 \
 *       \          \
 *        16 24 18   \
 *         \          \
 *          \          \
 *           \   -1 07 02
 *            \
 *             \ 11 20 14
 *              \
 *               03 15 06
 *
 * For each piece type, the IDs are ordered from top to bottom, front to back,
 * and clockwise. The IDs are unique between cubie types to make it easy to
 * tell when an edge is in a face slot, the ID values stored for each type are:
 *
 * -1 -  6  Corners
 *  7 - 18  Edges
 * 19 - 24  Faces
 *
 * You may have noticed that the first corner has a negative ID. This corner is
 * not stored, but always assumed to be fixed in the upper left. Without this
 * fixed corner there would be multiple solved states, making many operations
 * less efficient.
 *
 * Although we don't store the colors themselves in this internal
 * representation, here are the face colors:
 *
 *  ID   Dir   Color
 *  --  -----  -----
 *  19   Top    White
 *  20   Front  Red
 *  21   Left   Green
 *  22   Back   Orange
 *  23   Right  Blue
 *  24   Down   Yellow
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
    Cubie cubies[25];
} Cube;

static const int N_TURN_TYPES = 39;

extern const Cube solved_state;

/**
 * This enum can be used to identify either cubie slots in the cube, or for a
 * cubie ID (since the cubie ID is the cubie's placement at the solved state).
 * The letters indicating the faces (Up, Down, Front, Back, Left and Right) are
 * always in the order UDFBLR. For example, the corner cubie at the
 * intersection of the upper, front and left faces is identified as CUBIE_UFL.
 * The edge cubie at the intersection of the front and left faces is identified
 * as CUBIE_FL.
 *
 * Notice that CUBIE_UFL is -1 because it is not stored in the cubie list.
 */
enum CubieId {
    CUBIE_UFL=-1, CUBIE_UBL, CUBIE_UBR, CUBIE_UFR,
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
 * Return one or more solutions to the cube.
 *
 * Each solution is a list of integers (see Cube_turn() for documentation on
 * which turns the integers correspond to). Solutions are -1 delimited, with -2
 * at the very end.
 *
 * TODO: Option to return more than one solution.
 */
int* Cube_solve(const Cube* cube);

/**
 * Same as Cube_solve(), but gets the puzzle into a cube shape, instead of a
 * completely solved cube.
 */
int* Cube_solve_to_cube_shape(const Cube* cube);

/**
 * Print the cube as a list of (id, orientation).
 */
void Cube_print(FILE* out, const Cube* cube);

/**
 * Free a cube previously allocated with a Cube_new_* function.
 */
void Cube_free(Cube* cube);

#endif
