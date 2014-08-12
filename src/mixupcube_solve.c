
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>

#include "mixupcube.h"
#include "stack.h"
#include "solution_list.h"

// Private Prototypes
static int* solve(const Cube* cube, bool (*is_solved_func)(const Cube* cube));
static SolutionList* search_at_depth(
    const Cube* to_solve,
    int max_depth,
    Stack* stack,
    bool (*is_solved_func)(const Cube* cube),
    bool multiple_solutions);


int* Cube_solve(const Cube* cube) {
    return solve(cube, Cube_is_solved);
}

int* Cube_solve_to_cube_shape(const Cube* cube) {
    return solve(cube, &Cube_is_cube_shape);
}

static int* solve(const Cube* cube, bool (*is_solved_func)(const Cube* cube)) {
    // Depth first search implemented with iterative deepening
    Stack* stack = Stack_new(1000);
    SolutionList* solutions;
    int* ret;

    if(is_solved_func(cube)) {
        ret = (int*) calloc(1, sizeof(int));
        ret[0] = -2;
        Stack_free(stack);
        return ret;
    }

    for(int depth=1; ; depth++) {
        printf("Searching Depth %d...\n", depth);
        solutions = search_at_depth(cube, depth, stack, is_solved_func, false);
        if(SolutionList_count(solutions) > 0) {
            ret = SolutionList_get_int_list(solutions);
            SolutionList_free(solutions);
            Stack_free(stack);
            return ret;
        }
        SolutionList_free(solutions);
    }
}

static SolutionList* search_at_depth(
    const Cube* to_solve,
    int max_depth,
    Stack* stack,
    bool (*is_solved_func)(const Cube* cube),
    bool multiple_solutions)
{
    Cube current, tmp;
    int depth, turn;
    bool pop_successful;
    int path[max_depth];
    SolutionList* solutions = SolutionList_new();

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
                if(is_solved_func(&tmp)) {

                    // Solution Found!
                    path[max_depth-1] = i;
                    SolutionList_add(solutions, path, max_depth);
                    if(!multiple_solutions) {
                        return solutions;
                    }

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
            return solutions;
        }
        path[depth-1] = turn;

    }
}
