
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <assert.h>

#include "mixupcube.h"
#include "stack.h"
#include "solution_list.h"

/**
 * Possible next turns, given the previous turn.
 *
 * This is an optimization which avoids sequences of turns than are never
 * optimal, or can't reach a solution faster than another move that this table
 * does allow.
 *
 * Each integer represents the previous turn, and each bit represents the next
 * turn (from least to most significant bit). A 1 means avoid this turn, while
 * a 0 means it's ok. You can use it like this:
 *
 *    if(turn_avoid_table[previous_turn] & (1L << next_turn)) {
 *      // Avoid the turn
 *    } else {
 *      // Make the turn
 *    }
 *
 * When there is no last move, index 39 is used, which avoids nothing.
 *
 * DO NOT MODIFY THIS TABLE DIRECTLY. It is generated from
 * "generate_turn_avoid_table.py". See that file for a full description of
 * which turns are avoided and why.
 *
 */
static const unsigned long long int turn_avoid_table[40] = {
    0x24924830c3, 0x0000002082, 0x492490c30c, 0x0000008208, 0x1249270c30, 0x0000020820,
    0x24924830c3, 0x0000002082, 0x492490c30c, 0x0000008208, 0x1249270c30, 0x0000020820,
    0x24924830c3, 0x0000002082, 0x492490c30c, 0x0000008208, 0x1249270c30, 0x0000020820,
    0x1249260820, 0x2492482082, 0x4924908208,
    0x1249260820, 0x2492482082, 0x4924908208,
    0x1249260820, 0x2492482082, 0x4924908208,
    0x1249260820, 0x2492482082, 0x4924908208,
    0x1249260820, 0x2492482082, 0x4924908208,
    0x1249260820, 0x2492482082, 0x4924908208,
    0x1249260820, 0x2492482082, 0x4924908208,
    0x0000000000,
};

// Private Prototypes
static int* solve(const Cube* cube, bool (*is_solved_func)(const Cube* cube));
static SolutionList* search_at_depth(
    const Cube* to_solve,
    int max_depth,
    Stack* stack,
    bool (*is_solved_func)(const Cube* cube),
    bool multiple_solutions);

static unsigned long long int nodes_visited;


int* Cube_solve(const Cube* cube) {
    return solve(cube, Cube_is_solved);
}

int* Cube_solve_to_cube_shape(const Cube* cube) {
    return solve(cube, &Cube_is_cube_shape);
}

static int* solve(const Cube* cube, bool (*is_solved_func)(const Cube* cube)) {
    // Depth first search implemented with iterative deepening
    nodes_visited = 0;
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
        printf("%llu nodes visited\n", nodes_visited);
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
    turn = 39;
    Stack_clear(stack);
    while(1) {

        if(depth == max_depth-1) {
            // Don't push cubes at the last depth to the stack, just check if
            // they're solved.
            for(int i=0; i<N_TURN_TYPES; i++) {
                if(turn_avoid_table[turn] & (1L << i)) {
                    continue;
                }
                nodes_visited++;
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
                if(turn_avoid_table[turn] & (1L << i)) {
                    continue;
                }
                nodes_visited++;
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
