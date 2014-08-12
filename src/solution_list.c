
#include <stdlib.h>
#include <string.h>

#include "solution_list.h"


SolutionList* SolutionList_new() {
    SolutionList* s = malloc(sizeof(SolutionList));
    s->n_solutions = 0;
    s->n_ints = 1;
    s->solutions = (int*) malloc(sizeof(int));
    s->solutions[0] = -2;
    return s;
}

void SolutionList_free(SolutionList* s) {
    free(s->solutions);
    free(s);
}

void SolutionList_add(SolutionList* s, const int* solution, int len)
{
    if(s->n_solutions <= 0) {
        s->n_ints = len + 1;
        free(s->solutions);
        s->solutions = (int*) calloc(s->n_ints, sizeof(int));
        for(int i=0; i<len; i++) {
            s->solutions[i] = solution[i];
        }
        s->solutions[s->n_ints-1] = -2;
        s->n_solutions++;

    } else {
        int old_n_ints = s->n_ints;
        s->n_ints += len+1;
        s->solutions = (int*) realloc(s->solutions, (s->n_ints)*sizeof(int));
        s->solutions[old_n_ints-1] = -1;
        for(int i=0; i<len; i++) {
            s->solutions[i + old_n_ints] = solution[i];
        }
        s->solutions[s->n_ints-1] = -2;
        s->n_solutions++;

    }
}

int SolutionList_count(const SolutionList* s) {
    return s->n_solutions;
}

int* SolutionList_get_int_list(const SolutionList* s) {
    int* l = (int*) calloc(s->n_ints, sizeof(int));
    memcpy((void*) l, (void*) s->solutions, s->n_ints * sizeof(int));
    return l;
}
