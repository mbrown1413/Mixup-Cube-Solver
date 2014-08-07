
#ifndef STACK_H
#define STACK_H

#include <stdbool.h>

#include "mixupcube.h"

typedef struct {
    Cube cube;
    int turn;
    int depth;
} _StackNode;

typedef struct {
    int len;
    int allocated;
    _StackNode* nodes;
} Stack;

Stack* Stack_new(int initial_allocation);
void Stack_push(Stack* s, const Cube* c, int turn, int depth);
bool Stack_pop(Stack* s, Cube* cube_out, int* turn_out, int* depth_out);
bool Stack_peek(Stack* s, Cube* cube_out, int* turn_out, int* depth_out);
void Stack_clear(Stack* s);
void Stack_free(Stack* s);

#endif
