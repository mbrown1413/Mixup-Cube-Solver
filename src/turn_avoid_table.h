
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
