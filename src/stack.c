
#include <stdlib.h>

#include "stack.h"

Stack* Stack_new(int initial_allocation) {
    Stack* s = (Stack*) calloc(1, sizeof(Stack));
    s->len = 0;
    s->allocated = initial_allocation;
    s->nodes = (_StackNode*) calloc(initial_allocation, sizeof(_StackNode));
    return s;
}

void Stack_push(Stack* s, const Cube* c, int turn, int depth) {
    s->len++;
    if(s->len > s->allocated) {
        s->allocated = s->len + 100;
        s->nodes = (_StackNode*) realloc(s->nodes, s->allocated);
    }
    _StackNode* n = &s->nodes[s->len-1];
    n->cube = *c;
    n->depth = depth;
    n->turn = turn;
}

bool Stack_pop(Stack* s, Cube* cube_out, int* turn_out, int* depth_out) {
    if(s->len <= 0) {
        return false;
    }
    s->len -= 1;
    _StackNode* n = &s->nodes[s->len];
    *cube_out = n->cube;
    *depth_out = n->depth;
    *turn_out = n->turn;
    return true;
}

bool Stack_peek(Stack* s, Cube* cube_out, int* turn_out, int* depth_out) {
    if(s->len <= 0) {
        return false;
    }
    _StackNode* n = &s->nodes[s->len-1];
    *cube_out = n->cube;
    *depth_out = n->depth;
    *turn_out = n->turn;
    return true;
}

void Stack_clear(Stack* s) {
    s->len = 0;
}

void Stack_free(Stack* s) {
    free(s->nodes);
    free(s);
}
