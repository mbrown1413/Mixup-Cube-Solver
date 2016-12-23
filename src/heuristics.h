#ifndef HEURISTICS_H
#define HEURISTICS_H

/**
 * Generates and saves all heuristics tables to disk.
 *
 * Returns true if all tables were generated successfully.
 */
bool Heuristics_generate();

/**
 * Must be called before `Heuristics_get_dist()` to load heuristics tables.
 * Returns true on success or false on failure.
 */
bool Heuristics_load();

/**
 * Uses heuristics tables to get a lower bound on the distance `cube` is from
 * the solved state.
 */
uint8_t Heuristics_get_dist(const Cube* cube);


#endif
