#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "mixupcube.h"

// Private Prototypes
static bool Cubie_is_face(const Cubie* c);


static const Cube solved_cube = {{
    { 0, 0}, { 1, 0}, { 2, 0}, { 3, 0}, { 4, 0}, { 5, 0}, {6, 0}, {7, 0},
    { 8, 0}, { 9, 0}, {10, 0}, {11, 0}, {12, 0}, {13, 0},
    {14, 0}, {15, 0}, {16, 0}, {17, 0}, {18, 0}, {19, 0},
    {20, 0}, {21, 0}, {22, 0}, {23, 0}, {24, 0}, {25, 0}
}};


static bool Cubie_is_face(const Cubie* c) {
    return c->id >= 20;
}

Cube* Cube_new_solved() {
    Cube* c = (Cube*) malloc(sizeof(Cube));
    Cube_copy(c, &solved_cube);
    return c;
}

void Cube_copy(Cube* dst, const Cube* src) {
    memcpy((void*) dst, (void*) src, sizeof(Cube));
}

// Cube_turn() is located in mixupcube_turn.c

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
