#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "mixupcube.h"

// Private prototypes
static void Cubie_corner_rot(Cubie* c, int amount);
static void Cubie_edge_rot(Cubie* c, int amount);
static bool Cubie_is_face(const Cubie* c);
static void Cube_cycle_4(Cube* cube, enum CubieId c0, enum CubieId c1,
                                     enum CubieId c2, enum CubieId c3);
//static void Cube_cycle_8(Cube* cube,
//    enum CubieId c0, enum CubieId c1, enum CubieId c2, enum CubieId c3,
//    enum CubieId c4, enum CubieId c5, enum CubieId c6, enum CubieId c7);

static const Cube solved_cube = {{
    { 0, 0}, { 1, 0}, { 2, 0}, { 3, 0}, { 4, 0}, { 5, 0}, {6, 0}, {7, 0},
    { 8, 0}, { 9, 0}, {10, 0}, {11, 0}, {12, 0}, {13, 0},
    {14, 0}, {15, 0}, {16, 0}, {17, 0}, {18, 0}, {19, 0},
    {20, 0}, {21, 0}, {22, 0}, {23, 0}, {24, 0}, {25, 0}
}};


static void Cubie_corner_rot(Cubie* c, int amount) {
    c->orient = (c->orient + amount) % 3;
}

static void Cubie_edge_rot(Cubie* c, int amount) {
    c->orient = (c->orient + amount) % 4;
}

static bool Cubie_is_face(const Cubie* c) {
    return c->id >= 20;
}

/**
 * c0 replaces c1, which replaces c2, which replaces c3, which replaces c0.
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

/*
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
*/

Cube* Cube_new_solved() {
    Cube* c = (Cube*) malloc(sizeof(Cube));
    Cube_copy(c, &solved_cube);
    return c;
}

void Cube_copy(Cube* dst, const Cube* src) {
    memcpy((void*) dst, (void*) src, sizeof(Cube));
}

void Cube_turn(Cube* cube, int turn) {
    #define EDGE_ROT(cubie, amount) \
        Cubie_edge_rot(&cube->cubies[(cubie)], (amount))
    #define CORNER_ROT(cubie, amount) \
        Cubie_corner_rot(&cube->cubies[(cubie)], (amount))

    switch(turn) {
        case 0:  // U
            //TODO
        break;
        case 1:  // D
            //TODO
        break;
        case 2:  // F
            //TODO
        break;
        case 3:  // B
            //TODO
        break;
        case 4:  // L
            //CORNER_ROT(CUBIE_UFL, 2);
            //CORNER_ROT(CUBIE_UBL, );
            //CORNER_ROT(CUBIE_DBL, );
            //CORNER_ROT(CUBIE_DFL, );
        break;
        case 5:  // R
            CORNER_ROT(CUBIE_UFR, 1);
            CORNER_ROT(CUBIE_UBR, 2);
            CORNER_ROT(CUBIE_DFR, 2);
            CORNER_ROT(CUBIE_DBR, 1);
            EDGE_ROT(CUBIE_UR, 2);
            EDGE_ROT(CUBIE_BR, 2);
            EDGE_ROT(CUBIE_DR, 2);
            EDGE_ROT(CUBIE_FR, 2);
            EDGE_ROT(CUBIE_R, 1);
            Cube_cycle_4(cube, CUBIE_UFR, CUBIE_UBR, CUBIE_DBR, CUBIE_DFR);
            Cube_cycle_4(cube, CUBIE_UR, CUBIE_BR, CUBIE_DR, CUBIE_FR);
        break;
    }

    #undef EDGE_ROT
    #undef CORNER_ROT
}

bool Cube_is_cube_shape(const Cube* cube) {
    Cubie c;
    for(int i=8; i<20; i++) {
        c = cube->cubies[i];
        if(Cubie_is_face(&c) || c.orient == 1 || c.orient == 3) {
            return false;
        }
    }
    return true;
}

bool Cube_is_solved(const Cube* cube) {
    return false;
    /*
    Cube tmp;
    Cube_copy(&tmp, cube);

    Cube solved_cubes[6] = {
        XXX //TODO
    }

    // Zero face slot orientations
    // If it turns out there is an edge in a face slot, it doesn't matter:
    // we'll fail on the cubie IDs.
    for(int i=20; i<26; i++) {
        tmp->cubies[i].orient = 0;
    }

    // Compare with the 6 solved cubes
    for(int i=0; i<6; i++) {
        if(memcmp((void*) tmp, (void*) solved_cubes[i], sizeof(Cube)) == 0) {
            return true;
        }
    }

    return false;
    */
}

void Cube_print(FILE* out, const Cube* cube) {
    fprintf(out, "[");
    for(int i=0; i<26; i++) {
        Cubie cubie = cube->cubies[i];
        fprintf(out, "(%d, %d)", cubie.id, cubie.orient);
        if(i != 25) {
            fprintf(out, ", ");
        }
    }
    fprintf(out, "]\n");
}

void Cube_free(Cube* cube) {
    free(cube);
}
