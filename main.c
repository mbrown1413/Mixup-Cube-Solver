
#include "cube.h"

int main() {
    Cube* cube = Cube_new_solved();
    Cube_print(stdout, cube);
    Cube_turn(cube, 5);
    Cube_print(stdout, cube);
    Cube_free(cube);
}
