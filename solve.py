#!/usr/bin/python3

import sys
import time

from mixupcube import MixupCube, CubieMismatchError

def solve(cube, solve_type=None):
    print("Solving {}".format(cube))

    start_time = time.time()
    if solve_type is None:
        solution = cube.solve()
    elif solve_type == "to_cube":
        solution = cube.solve_to_cube_shape()
    else:
        raise ValueError("Huh, this shouldn't ever happen")
    end_time = time.time()
    if solution:
        print("Solution:", solution)
    else:
        print("Cube already solved")

    print("Solve took {}s".format(end_time - start_time))

def main():

    cube_str = ''.join(sys.argv[1:])
    cube = MixupCube.from_str(cube_str)
    solve(cube)

if __name__ == "__main__":
    main()
