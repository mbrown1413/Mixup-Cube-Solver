
#include <assert.h>

#include <mixupcube.h>

#define ROT(cubie, amount) \
    Cube_rotate_cubie(cube, cubie, amount)

// Private prototypes
static void Cube_rotate_cubie(Cube* cube, enum CubieId idx, int amount);
static void Cube_cycle_4(Cube* cube, enum CubieId c0, enum CubieId c1,
                                     enum CubieId c2, enum CubieId c3);
static void Cube_cycle_8(Cube* cube,
    enum CubieId c0, enum CubieId c1, enum CubieId c2, enum CubieId c3,
    enum CubieId c4, enum CubieId c5, enum CubieId c6, enum CubieId c7);
static void Cube_turn_U(Cube* cube);
static void Cube_turn_D(Cube* cube);
static void Cube_turn_F(Cube* cube);
static void Cube_turn_B(Cube* cube);
static void Cube_turn_L(Cube* cube);
static void Cube_turn_R(Cube* cube);
static void Cube_turn_M(Cube* cube);
static void Cube_turn_E(Cube* cube);
static void Cube_turn_S(Cube* cube);


static void Cube_rotate_cubie(Cube* cube, enum CubieId idx, int amount) {
    Cubie* c = &cube->cubies[idx];
    if(idx < 8) {
        c->orient = (c->orient + amount) % 3;  // Corner
    } else {
        c->orient = (c->orient + amount) % 4;  // Edge or face
    }
}

/**
 * c0 replaces c1
 * c1 replaces c2
 * c2 replaces c3
 * c3 replaces c0
 */
static void Cube_cycle_4(Cube* cube, enum CubieId c0, enum CubieId c1,
                                     enum CubieId c2, enum CubieId c3)
{
    Cubie tmp = cube->cubies[c3];
    cube->cubies[c3] = cube->cubies[c2];
    cube->cubies[c2] = cube->cubies[c1];
    cube->cubies[c1] = cube->cubies[c0];
    cube->cubies[c0] = tmp;
}

static void Cube_cycle_8(Cube* cube,
    enum CubieId c0, enum CubieId c1, enum CubieId c2, enum CubieId c3,
    enum CubieId c4, enum CubieId c5, enum CubieId c6, enum CubieId c7)
{
    Cubie tmp = cube->cubies[c7];
    cube->cubies[c7] = cube->cubies[c6];
    cube->cubies[c6] = cube->cubies[c5];
    cube->cubies[c5] = cube->cubies[c4];
    cube->cubies[c4] = cube->cubies[c3];
    cube->cubies[c3] = cube->cubies[c2];
    cube->cubies[c2] = cube->cubies[c1];
    cube->cubies[c1] = cube->cubies[c0];
    cube->cubies[c0] = tmp;
}


static void Cube_turn_U(Cube* cube) {
    ROT(CUBIE_U, 1);
    Cube_cycle_4(cube, CUBIE_UFL, CUBIE_UBL, CUBIE_UBR, CUBIE_UFR);
    Cube_cycle_4(cube, CUBIE_UF, CUBIE_UL, CUBIE_UB, CUBIE_UR);
}

static void Cube_turn_D(Cube* cube) {
    ROT(CUBIE_D, 1);
    Cube_cycle_4(cube, CUBIE_DFL, CUBIE_DFR, CUBIE_DBR, CUBIE_DBL);
    Cube_cycle_4(cube, CUBIE_DF, CUBIE_DR, CUBIE_DB, CUBIE_DL);
}

static void Cube_turn_L(Cube* cube) {
    ROT(CUBIE_UFL, 2);
    ROT(CUBIE_UBL, 1);
    ROT(CUBIE_DBL, 2);
    ROT(CUBIE_DFL, 1);
    ROT(CUBIE_UL, 2);
    ROT(CUBIE_BL, 2);
    ROT(CUBIE_DL, 2);
    ROT(CUBIE_FL, 2);
    ROT(CUBIE_L, 1);
    Cube_cycle_4(cube, CUBIE_UFL, CUBIE_DFL, CUBIE_DBL, CUBIE_UBL);
    Cube_cycle_4(cube, CUBIE_UL, CUBIE_FL, CUBIE_DL, CUBIE_BL);
}

static void Cube_turn_R(Cube* cube) {
    ROT(CUBIE_UFR, 1);
    ROT(CUBIE_UBR, 2);
    ROT(CUBIE_DFR, 2);
    ROT(CUBIE_DBR, 1);
    ROT(CUBIE_UR, 2);
    ROT(CUBIE_BR, 2);
    ROT(CUBIE_DR, 2);
    ROT(CUBIE_FR, 2);
    ROT(CUBIE_R, 1);
    Cube_cycle_4(cube, CUBIE_UFR, CUBIE_UBR, CUBIE_DBR, CUBIE_DFR);
    Cube_cycle_4(cube, CUBIE_UR, CUBIE_BR, CUBIE_DR, CUBIE_FR);
}

static void Cube_turn_F(Cube* cube) {
    ROT(CUBIE_UFL, 1);
    ROT(CUBIE_UFR, 2);
    ROT(CUBIE_DFR, 1);
    ROT(CUBIE_DFL, 2);
    ROT(CUBIE_F, 1);
    Cube_cycle_4(cube, CUBIE_UFL, CUBIE_UFR, CUBIE_DFR, CUBIE_DFL);
    Cube_cycle_4(cube, CUBIE_UF, CUBIE_FR, CUBIE_DF, CUBIE_FL);
}

static void Cube_turn_B(Cube* cube) {
    ROT(CUBIE_UBR, 1);
    ROT(CUBIE_UBL, 2);
    ROT(CUBIE_DBL, 1);
    ROT(CUBIE_DBR, 2);
    ROT(CUBIE_B, 1);
    Cube_cycle_4(cube, CUBIE_UBR, CUBIE_UBL, CUBIE_DBL, CUBIE_DBR);
    Cube_cycle_4(cube, CUBIE_UB, CUBIE_BL, CUBIE_DB, CUBIE_BR);
}

static void Cube_turn_M(Cube* cube) {
    ROT(CUBIE_UF, 2);
    ROT(CUBIE_DF, 2);
    ROT(CUBIE_DB, 2);
    ROT(CUBIE_UB, 2);
    Cube_cycle_8(cube, CUBIE_U, CUBIE_UF, CUBIE_F, CUBIE_DF,
                       CUBIE_D, CUBIE_DB, CUBIE_B, CUBIE_UB);
}

static void Cube_turn_E(Cube* cube) {
    ROT(CUBIE_FL, 1);
    ROT(CUBIE_BL, 2);
    ROT(CUBIE_BR, 3);
    ROT(CUBIE_FR, 2);
    ROT(CUBIE_F, 1);
    ROT(CUBIE_B, 3);
    Cube_cycle_8(cube, CUBIE_FL, CUBIE_F, CUBIE_FR, CUBIE_R,
                       CUBIE_BR, CUBIE_B, CUBIE_BL, CUBIE_L);
}

static void Cube_turn_S(Cube* cube) {
    ROT(CUBIE_UL, 1);
    ROT(CUBIE_UR, 1);
    ROT(CUBIE_DR, 3);
    ROT(CUBIE_DL, 3);
    ROT(CUBIE_U, 1);
    ROT(CUBIE_L, 3);
    ROT(CUBIE_R, 1);
    ROT(CUBIE_D, 3);
    Cube_cycle_8(cube, CUBIE_UL, CUBIE_U, CUBIE_UR, CUBIE_R,
                       CUBIE_DR, CUBIE_D, CUBIE_DL, CUBIE_L);
}

void Cube_turn(Cube* cube, int turn) {
    assert(turn >= 0 && turn < 39);

    if(turn < 18) {  // Face Turns
        // The moves are ordered such that 6-11 is the same 0-5, but repeated
        // twice. Same with 12-17, except repeated thrice. That makes this code
        // very compact.
        int times_to_repeat = 1 + turn / 6;
        for(int i=0; i<times_to_repeat; i++) {
            switch(turn % 6) {
                case 0:
                    Cube_turn_U(cube);
                break;
                case 1:
                    Cube_turn_D(cube);
                break;
                case 2:
                    Cube_turn_F(cube);
                break;
                case 3:
                    Cube_turn_B(cube);
                break;
                case 4:
                    Cube_turn_L(cube);
                break;
                case 5:
                    Cube_turn_R(cube);
                break;
            }
        }

    } else {  // Slice Turns
        int times_to_repeat = 1 + (turn - 18) / 3;
        for(int i=0; i<times_to_repeat; i++) {
            switch((turn - 18) % 3) {
                case 0:
                    Cube_turn_M(cube);
                break;
                case 1:
                    Cube_turn_E(cube);
                break;
                case 2:
                    Cube_turn_S(cube);
                break;
            }
        }
    }

}
