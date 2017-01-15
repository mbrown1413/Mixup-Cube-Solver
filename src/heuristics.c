
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "mixupcube.h"
#include "heuristics.h"
#include "stack.h"

#define N_HEURISTICS (sizeof(heuristics) / sizeof(heuristics[0]))

const char FILENAME_FORMAT[] = "heuristics/%s.ht";

typedef struct {
    const char* name;

    // Hash values must be in the range 0 to size-1. The hash function must
    // have zero collisions and cover the entire range without any holes (or
    // else the table generation will never stop searching for the last hash
    // value).
    uint64_t (*hash_func)(const Cube* cube);
    uint64_t size;

    // Optimizations should only be enabled after it has been shown they do not
    // affect the resulting table at all.
    bool instack_optimization;
    bool valid_turns_optimization;

} Heuristic;

// Private Prototypes
static const Heuristic* Heuristic_get_by_name(const char* name);
static char* Heuristic_get_filename(const char* name);
static uint8_t* Heuristic_gen_table(const Heuristic* h);
static uint64_t hash_corners(const Cube* cube);
static uint64_t hash_edges_1(const Cube* cube);
static uint64_t hash_edges_2(const Cube* cube);
static uint64_t hash_edges_3(const Cube* cube);
static uint64_t hash_edges_4(const Cube* cube);
static uint64_t hash_edges_5(const Cube* cube);
static uint64_t hash_edges_6(const Cube* cube);
static uint64_t hash_faces1(const Cube* cube);
static uint64_t hash_faces2(const Cube* cube);

// Stores all available heuristics
static const Heuristic heuristics[] = {

    // Corner Heuristic
    // Complete state of all corners. This actually only hashes 6 corners,
    // since UFL is fixed in place, and the last corner's position and
    // orientation are determined by the others.
    {
        "corners",
        // sha1sum: b899ecf20a87dc5366225c6e14b9477b4011bcd955cc89c2dcbb2dfffcb225cf
        hash_corners,
        (7*6*5*4*3*2) * (3*3*3*3*3*3),  // 7! * 3^6 = 3674160
        true, true
    },

    // Edge Heuristics
    // Each of these includes 4 edges and one face slot. Some edges are covered
    // more than once, but each face is covered exactly once.
    {
        "edges1",
        // sha1sum: 7b3bed30fdca80832a682a37df203a8ecbab86911ab51c19cd676804dd88e7b0
        hash_edges_1,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    },
    {
        "edges2",
        hash_edges_2,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    },
    {
        "edges3",
        hash_edges_3,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    },
    {
        "edges4",
        hash_edges_4,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    },
    {
        "edges5",
        hash_edges_5,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    },
    {
        "edges6",
        hash_edges_6,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    },

    // Faces
    // Numbers are the same as edges, but only faces are included.
    {
        "faces1",
        hash_faces1,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    },
    {
        "faces2",
        hash_faces2,
        (18*17*16*15) * 4*4*4*4,  // 18! / 14! * 4^4 = 18800640
        false, false
    }
};

// Stores loaded heuristics
static struct {
    uint64_t (*hash_func)(const Cube* cube);
    uint64_t size;
    uint8_t* table;
} active[N_HEURISTICS];
static int n_active;


/***** Public Functions *****/

bool Heuristic_generate(const char* name) {
    const Heuristic* h = Heuristic_get_by_name(name);
    if(h == NULL) {
        fprintf(stderr, "Error: No heuristic by name \"%s\"\n", name);
        return false;
    }

    // Generate
    char* filename = Heuristic_get_filename(name);
    printf("Generating %s\n", filename);
    uint8_t* table = Heuristic_gen_table(h);
    if(table == NULL) {
        free(filename);
        return false;
    }

    // Save to file
    FILE* fp = fopen(filename, "w");
    if (fp == NULL) {
        fprintf(stderr, "Error: Could not open heuristic file \"%s\" for writing.\n",
                filename);
        free(filename);
        free(table);
        return false;
    }
    if(fwrite(table, sizeof(uint8_t)*h->size, 1, fp) != 1) {
        fprintf(stderr, "Error: Write to heuristic file \"%s\" failed.\n",
                filename);
        fclose(fp);
        free(filename);
        free(table);
        return false;
    }
    fclose(fp);

    free(filename);
    free(table);
    return true;
}

bool Heuristic_load(const char* name) {
    const Heuristic* h = Heuristic_get_by_name(name);
    if(h == NULL) {
        return false;
    }
    char* filename = Heuristic_get_filename(name);

    FILE* fp = fopen(filename, "r");
    if (fp == NULL) {
        fprintf(stderr, "Heuristic file not found: \"%s\"\n", filename);
        free(filename);
        static bool hinted = false;
        if(!hinted) {
            printf("Hint: See README for how to obtain heuristics tables,\n");
            printf("      solving may be very slow without them!\n");
            hinted = true;
        }
        return false;
    }
    uint8_t* table = (uint8_t*) malloc(sizeof(uint8_t)*h->size);
    if (fread(table, sizeof(uint8_t)*h->size, 1, fp) != 1) {
        fprintf(stderr, "Error: Read from heuristic file \"%s\" failed.\n",
                filename);
        free(filename);
        fclose(fp);
        return false;
    }
    free(filename);
    fclose(fp);

    // Save into `active`
    active[n_active].hash_func = h->hash_func;
    active[n_active].size = h->size;
    active[n_active].table = table;
    n_active++;

    return true;
}

void Heuristics_load_all() {
    for(int i=0; i<N_HEURISTICS; i++) {
        Heuristic_load(heuristics[i].name);
    }
}

void Heuristics_unload_all() {
    for(int i=0; i<n_active; i++) {
        active[i].hash_func = NULL;
        active[i].size = 0;
        free(active[i].table);
        active[i].table = NULL;
    }
    n_active = 0;
}


uint8_t Heuristics_get_dist(const Cube* cube) {
    uint8_t dist, max_dist = 0;
    for(int i=0; i<n_active; i++) {

        dist = active[i].table[active[i].hash_func(cube)];
        if(dist > max_dist) {
            max_dist = dist;
        }

    }
    return max_dist;
}


/***** Private Functions *****/

static const Heuristic* Heuristic_get_by_name(const char* name) {
    for(int i=0; i<N_HEURISTICS; i++) {
        if(strcmp(name, heuristics[i].name) == 0) {
            return &heuristics[i];
            break;
        }
    }
    return NULL;
}

static char* Heuristic_get_filename(const char* name) {
    int length = strlen(name)+strlen(FILENAME_FORMAT);
    char* filename = malloc(sizeof(char)*length);
    snprintf(filename, length, FILENAME_FORMAT, name);
    return filename;
}

static uint8_t* Heuristic_gen_table(const Heuristic* h) {
    Cube cube, tmp_cube;
    int depth, turn, n_visited=0;
    uint64_t hash;
    uint8_t* table = (uint8_t*) calloc(h->size, sizeof(uint8_t));
    Stack* stack = Stack_new(1000);

    // Keeps track of which entries in the table are filled
    bool* visited = (bool*) calloc(h->size, sizeof(bool));

    // At each max_depth, keep track of which hashes have already been visited
    // and at what depth. We don't have to search further if a cube's hash has
    // been visited at a lesser depth. This reduces the number of states
    // searched significantly.
    //
    // This works like brownan's Rubik's Cube solver:
    //     https://github.com/brownan/Rubiks-Cube-Solver/blob/master/cornertable.c#L138
    uint8_t* instack = NULL;
    if(h->instack_optimization) {
        instack = (uint8_t*) calloc(h->size, sizeof(uint8_t));
    }

    // Figure out which turns actually change the hash value. Only consider
    // those turns.
    bool valid_turns[N_TURN_TYPES];
    if(h->valid_turns_optimization) {
        for(int i=0; i<N_TURN_TYPES; i++) {
            Cube_copy(&tmp_cube, &solved_state);
            Cube_turn(&tmp_cube, i);
            if(h->hash_func(&tmp_cube) == h->hash_func(&solved_state)) {
                valid_turns[i] = false;
            } else {
                valid_turns[i] = true;
            }
        }
    }

    // Iterative deepening breadth-first search
    for(int max_depth=0; n_visited < h->size; max_depth++) {
        printf("%d / %lu\n", n_visited, h->size);
        printf("Searching Depth %d\n", max_depth);
        Stack_push(stack, &solved_state, 0, 0);

        if(instack) {
            memset(instack, 0, h->size*sizeof(uint8_t));
        }

        while(Stack_pop(stack, &cube, &turn, &depth)) {

            hash = h->hash_func(&cube);
            if(hash >= h->size) {
                fprintf(stderr, "Error: Hash value too large: %lu\n", hash);
                if(instack) { free(instack); }
                free(table);
                free(visited);
                return NULL;
            }

            if(instack) {
                if(instack[hash] != 0 && instack[hash] <= depth) {
                    continue;
                }
                instack[hash] = depth;
            }

            if(depth != max_depth) {

                // Push turned cubes to the stack
                for(int i=N_TURN_TYPES-1; i>=0; i--) {
                    if(h->valid_turns_optimization && !valid_turns[i]) {
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

    if(instack) { free(instack); }
    free(visited);
    return table;
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

static uint64_t hash_edges_generic(const Cube* cube, const uint8_t cubie_ids[4]) {
    uint64_t result = 0;
    uint64_t max = 1;

    uint8_t ids[4];
    uint8_t orients[4];
    for(int i=0; i<4; i++) {
        ids[i] = cube->cubies[cubie_ids[i]].id - 7;
        orients[i] = cube->cubies[cubie_ids[i]].orient;
    }

    for(int i=0; i<4; i++) {
        result += max*ids[i];
        max *= 18-i;
        for(int j=i+1; j<4; j++) {
            if(ids[j] > ids[i]) {
                ids[j]--;
            }
        }
    }

    for(int i=0; i<4; i++) {
        result += max*orients[i];
        max *= 4;
    }

    return result;
}

static uint64_t hash_edges_1(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_U, CUBIE_UF, CUBIE_DR, CUBIE_BL
    };
    return hash_edges_generic(cube, cubies);
}

static uint64_t hash_edges_2(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_L, CUBIE_FL, CUBIE_UR, CUBIE_DB
    };
    return hash_edges_generic(cube, cubies);
}

static uint64_t hash_edges_3(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_D, CUBIE_DF, CUBIE_UL, CUBIE_BR
    };
    return hash_edges_generic(cube, cubies);
}

static uint64_t hash_edges_4(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_R, CUBIE_FR, CUBIE_DL, CUBIE_UB
    };
    return hash_edges_generic(cube, cubies);
}

static uint64_t hash_edges_5(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_F, CUBIE_DF, CUBIE_FR, CUBIE_UL,
    };
    return hash_edges_generic(cube, cubies);
}

static uint64_t hash_edges_6(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_B, CUBIE_UB, CUBIE_BR, CUBIE_DL,
    };
    return hash_edges_generic(cube, cubies);
}

static uint64_t hash_faces1(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_U, CUBIE_D, CUBIE_L, CUBIE_R
    };
    return hash_edges_generic(cube, cubies);
}

static uint64_t hash_faces2(const Cube* cube) {
    const uint8_t cubies[4] = {
        CUBIE_U, CUBIE_D, CUBIE_F, CUBIE_B
    };
    return hash_edges_generic(cube, cubies);
}
