/**
 * Heuristics allow a solution search to prune nodes that can never reach a
 * solution in the current depth being searched at. It works by looking at a
 * subset of the cube to see how many turns it would take to solve that subset.
 * These heuristics are expensive to compute, so naturally they are precomputed
 * and stored in a table.
 *
 * Internally, a list of active heuristics is stored. Calling
 * `Heuristic_load()` or `Heuristics_load_all()` can be used to load a specific
 * heuristic, or all. In order to load a heuristic, the heuristic table must be
 * generated and stored on disk using `Heuristic_generate()`, which only needs
 * to be done once.
 */

#ifndef HEURISTICS_H
#define HEURISTICS_H

/**
 * Generates and saves heuristic tables to disk. `name` should be the name of a
 * heuristic table.
 *
 * Returns true if all tables were generated successfully.
 */
bool Heuristic_generate(const char* name);

/**
 * Loads one heuristic identified by name.
 *
 * Returns true on success or false on failure.
 */
bool Heuristic_load(const char* name);

/**
 * Load all heuristics.
 *
 * If a heuristic is not available, it is ignored.
 */
void Heuristics_load_all();

/**
 * Unloads all heuristics.
 */
void Heuristics_unload_all();

/**
 * Gets a lower bound on the distance `cube` is from the solved state using the
 * currently active heuristics.
 */
uint8_t Heuristics_get_dist(const Cube* cube);

#endif
