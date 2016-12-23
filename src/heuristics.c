/**
 * Heuristics allow a solution search to prune nodes that can never reach a
 * solution in the current depth being searched at. It works by looking at a
 * subset of the cube to see how many turns it would take to solve that subset.
 * These heuristics are expensive to compute, so naturally they are precomputed
 * and stored in a table.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "mixupcube.h"
#include "heuristics.h"
#include "stack.h"

#define N_HEURISTICS (sizeof(heuristics) / sizeof(heuristics[0]))

typedef struct {
    const char* filename;

    // Hash values must be in the range 0 to size-1. The hash function must
    // have zero collisions and cover the entire range without any holes (or
    // else the table generation will never stop searching for the last hash
    // value).
    uint64_t (*hash_func)(const Cube* cube);
    uint64_t size;

    // Lookup table holding the solve distance for every value of the hash.
    // Initialize to NULL, it will be loaded later.
    uint8_t* table;

} Heuristic;

// Private Prototypes
static uint8_t* Heuristic_generate(Heuristic* h);
static bool Heuristic_save(Heuristic* h);
static bool Heuristic_load(Heuristic* h);
static bool Heuristic_unload(Heuristic* h);
static uint64_t hash_corners(const Cube* cube);

static Heuristic heuristics[] = {
    {
        "heuristics/corner.ht",
        hash_corners,
        (7*6*5*4*3*2) * (3*3*3*3*3*3),  // 7! * 3^6 = 3674160
        NULL
    },
};


/***** Public Functions *****/

bool Heuristics_generate() {
    for(int i=0; i<N_HEURISTICS; i++) {
        Heuristic* h = &heuristics[i];
        h->table = Heuristic_generate(h);
        if(h->table == NULL) {
            fprintf(stderr, "Error generating heuristic \"%s\"\n", h->filename);
            return false;
        }

        Heuristic_save(h);
        Heuristic_unload(h);

        free(h->table);
        h->table = NULL;
    }
    return true;
}

bool Heuristics_load() {
    bool load_successful;
    for(int i=0; i<N_HEURISTICS; i++) {
        Heuristic* h = &heuristics[i];

        load_successful = Heuristic_load(h);
        if(!load_successful) {
            fprintf(stderr, "Could not load table from file \"%s\"\n",
                    h->filename);
            return false;
        }

    }
    return true;
}

uint8_t Heuristics_get_dist(const Cube* cube) {
    uint8_t dist, max_dist = 0;
    for(int i=0; i<N_HEURISTICS; i++) {
        Heuristic* h = &heuristics[i];

        dist = h->table[h->hash_func(cube)];
        if(dist > max_dist) {
            max_dist = dist;
        }

    }
    return max_dist;
}


/***** Private Functions *****/

static uint8_t* Heuristic_generate(Heuristic* h) {
    Cube cube, tmp_cube;
    int depth, turn, n_visited=0;
    uint64_t hash;
    uint8_t* table = (uint8_t*) calloc(h->size, sizeof(uint8_t));
    Stack* stack = Stack_new(1000);

    // Keeps track of which entries in the table are filled
    bool* visited = (bool*) calloc(h->size, sizeof(bool));

    // At each max_depth, keep track of which hashes have already been visited
    // and at what depth.  We don't have to search further if a cube's hash has
    // been visited at a lesser depth. This reduces the number of states
    // searched significantly.
    //
    //TODO: This might not hold for all heuristic hashes. For example, ones
    //      that don't hash all corners or all edges. In this case, it might be
    //      nessesary to make a turn that does not effect the hash to get to
    //      some hash values.
    //
    // This works like brownan's Rubik's Cube solver:
    //     https://github.com/brownan/Rubiks-Cube-Solver/blob/master/cornertable.c#L138
    uint8_t* instack = (uint8_t*) calloc(h->size, sizeof(uint8_t));

    // Figure out which turns actually change the hash value. Only consider
    // those turns.
    //
    // TODO: This might make some heuristics never finish generating.
    bool valid_turns[N_TURN_TYPES];
    for(int i=0; i<N_TURN_TYPES; i++) {
        Cube_copy(&tmp_cube, &solved_state);
        Cube_turn(&tmp_cube, i);
        if(h->hash_func(&tmp_cube) == h->hash_func(&solved_state)) {
            valid_turns[i] = false;
        } else {
            valid_turns[i] = true;
        }
    }

    // Iterative deepening breadth-first search
    for(int max_depth=0; n_visited < h->size; max_depth++) {
        printf("Searching Depth %d\n", max_depth);
        Stack_push(stack, &solved_state, 0, 0);

        memset(instack, 0, h->size*sizeof(uint8_t));

        while(Stack_pop(stack, &cube, &turn, &depth)) {

            hash = h->hash_func(&cube);
            if(hash >= h->size) {
                fprintf(stderr, "Hash value too large: %lu\n", hash);
                free(instack);
                free(table);
                free(visited);
                return NULL;
            }

            if(instack[hash] != 0 && instack[hash] <= depth) {
                continue;
            }
            instack[hash] = depth;

            if(depth != max_depth) {

                // Push turned cubes to the stack
                for(int i=N_TURN_TYPES-1; i>=0; i--) {
                    if(!valid_turns[i]) {
                        continue;
                    }
                    Cube_copy(&tmp_cube, &cube);
                    Cube_turn(&tmp_cube, i);
                    Stack_push(stack, &tmp_cube, i, depth+1);
                }

            } else if (!visited[hash]) {

                visited[hash] = true;
                table[hash] = depth;
                n_visited += 1;

                if(n_visited % 100000 == 0) {
                    printf("%d / %lu\n", n_visited, h->size);
                }
                if(n_visited >= h->size) {
                    break;
                }

            }

        }
    }

    free(instack);
    free(visited);
    return table;
}

static bool Heuristic_save(Heuristic* h) {
    FILE* fp = fopen(h->filename, "w");
    if (fp == NULL) {
        fprintf(stderr, "Could not open heuristic file \"%s\" for writing.\n",
                h->filename);
        return false;
    }
    if(fwrite(h->table, sizeof(uint8_t)*h->size, 1, fp) != 1) {
        fprintf(stderr, "Write to heuristic file \"%s\" failed.\n",
                h->filename);
        fclose(fp);
        return false;
    }
    fclose(fp);
    return true;
}

static bool Heuristic_load(Heuristic* h) {
    if(h->table != NULL) { return true; }
    FILE* fp = fopen(h->filename, "r");
    if (fp == NULL) {
        fprintf(stderr, "Could not open heuristic file \"%s\" for reading.\n",
                h->filename);
        return false;
    }
    h->table = (uint8_t*) malloc(sizeof(uint8_t)*h->size);
    if (fread(h->table, sizeof(uint8_t)*h->size, 1, fp) != 1) {
        fprintf(stderr, "Read from heuristic file \"%s\" failed.\n",
                h->filename);
        fclose(fp);
        return false;
    }
    fclose(fp);
    return true;
}

static bool Heuristic_unload(Heuristic* h) {
    free(h->table);
    h->table = NULL;
    return true;
}


/***** Hash Functions *****/

static uint64_t hash_corners(const Cube* cube) {
    uint64_t result = 0;
    uint64_t max = 1;

    uint8_t ids[6];
    uint8_t orients[6];
    for(int i=0; i<6; i++) {
        ids[i] = cube->cubies[i].id;
        orients[i] = cube->cubies[i].orient;
    }

    for(int i=0; i<6; i++) {
        result += max*ids[i];
        max *= 7-i;
        for(int j=i+1; j<6; j++) {
            if(ids[j] > ids[i]) {
                ids[j]--;
            }
        }
    }

    for(int i=0; i<6; i++) {
        result += max*orients[i];
        max *= 3;
    }

    return result;
}
