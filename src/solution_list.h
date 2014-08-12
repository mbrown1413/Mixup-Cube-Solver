/**
 * A SolutionList is a list of solutions, where each solution is a list of
 * positive integers. It is stored as a single list of integers, where each
 * solution is separated by a -1. The end is marked with -2.
 */

#ifndef SOLUTION_LIST_H
#define SOLUTION_LIST_H

typedef struct {
    int n_solutions;
    int n_ints;  // Includes -1 and -2 delimiters
    int* solutions;
} SolutionList;

SolutionList* SolutionList_new();
void SolutionList_free(SolutionList* solutions);

/**
 * Add the list of integers at `solution` of length `len` to the solution list.
 */
void SolutionList_add(SolutionList* solutions, const int* solution, int len);

/**
 * Return the number of solutions in `solutions`.
 */
int SolutionList_count(const SolutionList* solutions);

/**
 * Return a copy of the integer list used to store the solutions. See the top
 * of this file for a description of how the integers are stored.
 */
int* SolutionList_get_int_list(const SolutionList* solutions);

#endif
