#!/usr/bin/python3
import mixupcube

c = mixupcube.MixupCube()
print(c)
c.turn("R")
print(c.is_cube_shape())
print(c.is_solved())
print(c)
