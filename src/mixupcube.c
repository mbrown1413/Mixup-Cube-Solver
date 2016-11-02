#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "mixupcube.h"

// Private Prototypes
static bool Cubie_is_face(const Cubie* c);


const Cube solved_state = {{
    { 0, 0}, { 1, 0}, { 2, 0}, { 3, 0}, { 4, 0}, { 5, 0}, {6, 0}, {7, 0},
    { 8, 0}, { 9, 0}, {10, 0}, {11, 0}, {12, 0}, {13, 0},
    {14, 0}, {15, 0}, {16, 0}, {17, 0}, {18, 0}, {19, 0},
    {20, 0}, {21, 0}, {22, 0}, {23, 0}, {24, 0}, {25, 0}
}};

static const Cube solved_states[6] = {
    {{  // White faces up
        { 0, 0}, { 1, 0}, { 2, 0}, { 3, 0}, { 4, 0}, { 5, 0}, {6, 0}, {7, 0},
        { 8, 0}, { 9, 0}, {10, 0}, {11, 0}, {12, 0}, {13, 0},
        {14, 0}, {15, 0}, {16, 0}, {17, 0}, {18, 0}, {19, 0},
        {20, 0}, {21, 0}, {22, 0}, {23, 0}, {24, 0}, {25, 0}
    }},
    {{  // White faces front
        { 1, 1}, { 5, 2}, { 6, 1}, { 2, 2}, { 0, 2}, { 4, 1}, {7, 2}, {3, 1},
        {10, 2}, {13, 2}, {18, 2}, {14, 2}, { 9, 2}, {17, 2},
        {19, 2}, {11, 2}, { 8, 2}, {12, 2}, {16, 2}, {15, 2},
        {23, 0}, {20, 0}, {22, 0}, {25, 0}, {24, 0}, {21, 0}
    }},
    {{  // White faces left
        { 3, 2}, { 2, 1}, { 6, 2}, { 7, 1}, { 0, 1}, { 1, 2}, {5, 1}, {4, 2},
        {15, 0}, {11, 2}, {14, 0}, {19, 2}, { 8, 0}, {10, 0},
        {18, 0}, {16, 0}, {12, 0}, { 9, 2}, {13, 0}, {17, 2},
        {24, 0}, {21, 0}, {20, 0}, {23, 0}, {25, 0}, {22, 0}
    }},
    {{  // White faces back
        { 4, 1}, { 0, 2}, { 3, 1}, { 7, 2}, { 5, 2}, { 1, 1}, {2, 2}, {6, 1},
        {16, 2}, {12, 2}, { 8, 2}, {15, 2}, {17, 2}, { 9, 2},
        {11, 2}, {19, 2}, {18, 2}, {13, 2}, {10, 2}, {14, 2},
        {21, 0}, {25, 0}, {22, 0}, {20, 0}, {24, 0}, {23, 0}
    }},
    {{  // White faces right
        { 4, 2}, { 5, 1}, { 1, 2}, { 0, 1}, { 7, 1}, { 6, 2}, {2, 1}, {3, 2},
        {12, 0}, {17, 2}, {13, 0}, { 9, 2}, {16, 0}, {18, 0},
        {10, 0}, { 8, 0}, {15, 0}, {19, 2}, {14, 0}, {11, 2},
        {22, 0}, {21, 0}, {25, 0}, {23, 0}, {20, 0}, {24, 0}
    }},
    {{  // White faces down
        { 5, 0}, { 4, 0}, { 7, 0}, { 6, 0}, { 1, 0}, { 0, 0}, {3, 0}, {2, 0},
        {18, 0}, {17, 0}, {16, 0}, {19, 0}, {13, 0}, {12, 0},
        {15, 0}, {14, 0}, {10, 0}, { 9, 0}, { 8, 0}, {11, 0},
        {25, 0}, {23, 0}, {22, 0}, {21, 0}, {24, 0}, {20, 0}
    }}
};


static bool Cubie_is_face(const Cubie* c) {
    return c->id >= 20;
}

Cube* Cube_new_solved() {
    Cube* c = (Cube*) malloc(sizeof(Cube));
    Cube_copy(c, &solved_state);
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
    Cube tmp;
    Cube_copy(&tmp, cube);

    // Zero face slot orientations
    // If it turns out there is an edge in a face slot, it doesn't matter,
    // we'll fail on the cubie IDs.
    for(int i=20; i<26; i++) {
        tmp.cubies[i].orient = 0;
    }

    // Compare with the 6 solved cubes
    for(int i=0; i<6; i++) {
        if(memcmp((void*) &tmp, (void*) &solved_states[i], sizeof(Cube)) == 0) {
            return true;
        }
    }

    return false;
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
