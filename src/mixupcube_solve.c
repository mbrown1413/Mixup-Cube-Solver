
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include "mixupcube.h"
#include "stack.h"

// Private Prototypes
static int* search_at_depth(const Cube* to_solve, int max_depth, Stack* stack);


int* Cube_solve(const Cube* cube, int* solution_length_out) {
    // Depth first search implemented with iterative deepening
    Stack* stack = Stack_new(1000);
    int* solution;

    if(Cube_is_solved(cube)) {
        solution = (int*) calloc(1, sizeof(int));
        solution[0] = -1;
        if(solution_length_out != NULL) {
            *solution_length_out = 0;
        }
        Stack_free(stack);
        return solution;
    }

    for(int d=1; ; d++) {
        solution = search_at_depth(cube, d, stack);
        if(solution != NULL) {
            if(solution_length_out != NULL) {
                *solution_length_out = d;
            }
            Stack_free(stack);
            return solution;
        }
    }
    Stack_free(stack);
    return NULL;
}

static int* search_at_depth(const Cube* to_solve, int max_depth, Stack* stack) {
    Cube current, tmp;
    int depth, turn;
    int* solution;
    bool pop_successful;
    int path[max_depth];

    assert(max_depth >= 0);

    current = *to_solve;
    depth = 0;
    Stack_clear(stack);
    while(1) {

        if(depth == max_depth-1) {
            // Don't push cubes at the last depth to the stack, just check if
            // they're solved.
            for(int i=0; i<N_TURN_TYPES; i++) {
                Cube_copy(&tmp, &current);
                Cube_turn(&tmp, i);
                if(Cube_is_solved(&tmp)) {

                    // Solution Found!
                    path[max_depth-1] = i;
                    goto found_solution;

                }
            }

        } else {

            // Push all possible turned cubes to the stack
            for(int i=0; i<N_TURN_TYPES; i++) {
                Cube_copy(&tmp, &current);
                Cube_turn(&tmp, i);
                Stack_push(stack, &tmp, i, depth+1);
            }

        }

        pop_successful = Stack_pop(stack, &current, &turn, &depth);
        if(!pop_successful) {
            return NULL;
        }
        path[depth-1] = turn;

    }

found_solution:
    solution = (int*) calloc(max_depth+1, sizeof(int));
    memcpy((void*) solution, (void*) path, sizeof(int)*(max_depth));
    solution[max_depth] = -1;
    return solution;

}
